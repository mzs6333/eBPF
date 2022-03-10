#define KBUILD_MODNAME "udp_cache"
#include <linux/bpf.h>
#include <linux/if_ether.h>
#include <linux/ip.h>
#include <linux/udp.h>
#include <linux/in.h>
#include <linux/if_packet.h>
#include <linux/if_vlan.h>
#include <linux/types.h>

#define CURRENT_PORT_NUMBER 51141
#define CACHE_SIZE 6
#define MAX_UDP_LENGTH 1480

typedef struct {
    int accessedSinceUpdate;
    char responsePayload;
} cache_response;

BPF_HISTOGRAM(counter, u64);
BPF_HASH(cache, char, cache_response, CACHE_SIZE);

int udp_cache(struct xdp_md *ctx)
{
    void *data = (void *)(long)ctx->data;
    void *data_end = (void *)(long)ctx->data_end;
    struct ethhdr *eth = data;
    __u64 nh_off = sizeof(*eth);
    __be32 dest_ip, src_ip;
    __be16 dest_port, src_port;
    __u16 h_proto;
    unsigned char dest_mac[ETH_ALEN];
    unsigned char source_mac[ETH_ALEN];

    if ((void *)eth + nh_off <= data_end)
    {
        
        struct iphdr *ip = data + nh_off;
        if ((void *)ip + sizeof(*ip) <= data_end)
        {
            
            if (ip->protocol == IPPROTO_UDP)
            {
                
                struct udphdr *udp = (void *)ip + sizeof(*ip);
                if ((void *)udp + sizeof(*udp) <= data_end)
                {

                    u64 value = htons(udp->dest);
                    if (value == CURRENT_PORT_NUMBER) {
                        counter.increment(value);
                        char *payload = data + sizeof(*eth) + sizeof(*ip) + sizeof(*udp);
                        if ( payload + 1 > data_end )
                            return XDP_PASS;
                        char payloadByte = payload[0];

                        cache_response *cacheResponsePtr = cache.lookup(&payloadByte);
                        if (cacheResponsePtr) {
                            char responsePayload = cacheResponsePtr->responsePayload;
                            memcpy(payload, &responsePayload, sizeof(char));
                            cacheResponsePtr->accessedSinceUpdate++;

                            memcpy(dest_mac, eth->h_dest, ETH_ALEN);
                            memcpy(source_mac, eth->h_source, ETH_ALEN);
                            dest_port = udp->dest;
                            src_port = udp->source;
                            dest_ip = ip->daddr;
                            src_ip = ip->saddr;
                            
                            memcpy(&(ip->daddr), &src_ip, sizeof(eth->h_dest));
                            memcpy(&(ip->saddr), &dest_ip, sizeof(eth->h_source));

                            memcpy(&(udp->dest), &src_port, sizeof(udp->dest));
                            memcpy(&(udp->source), &dest_port, sizeof(udp->source));

                            memcpy(&(eth->h_dest), &source_mac, sizeof(eth->h_dest));
                            memcpy(&(eth->h_source), &dest_mac, sizeof(eth->h_source));

                            // Compute UDP Checksum:

                            udp->check = 0;
                            u32 csum_buffer = 0;
                            u16 *buf = (void *)udp;

                            // Compute pseudo-header checksum
                            csum_buffer += (u16)ip->saddr;
                            csum_buffer += (u16)(ip->saddr >> 16);
                            csum_buffer += (u16)ip->daddr;
                            csum_buffer += (u16)(ip->daddr >> 16);
                            csum_buffer += (u16)ip->protocol << 8;
                            csum_buffer += udp->len;

                            // Compute checksum on udp header + payload
                            for (int i = 0; i < MAX_UDP_LENGTH; i += 2) {
                                if ((void *)(buf + 1) > data_end) {
                                    break;
                                }
                                csum_buffer += *buf;
                                buf++;
                            }
                            if ((void *)buf + 1 <= data_end) {
                                // In case payload is not 2 bytes aligned
                                csum_buffer += *(u8 *)buf;
                            }

                            u16 csum = (u16)csum_buffer + (u16)(csum_buffer >> 16);
                            csum = ~csum;

                            udp->check = csum;
                            
                            return XDP_TX;
                        }
                        else {
                            char cacheSizeIndex = '\x00';
                            cache_response *currentCacheSize = cache.lookup(&cacheSizeIndex);
                            if (!currentCacheSize)
                                return XDP_PASS;
                            int cacheSize = currentCacheSize->accessedSinceUpdate;
                            
                            if (cacheSize < CACHE_SIZE) {
                                char newCacheEntryFlag = '\n';
                                cache_response *newCacheEntry = cache.lookup(&newCacheEntryFlag);
                                if (!newCacheEntry)
                                    return XDP_PASS;
                                newCacheEntry->responsePayload = payloadByte;
                                currentCacheSize->responsePayload = 'p';
                                currentCacheSize->accessedSinceUpdate = currentCacheSize->accessedSinceUpdate + 1;
                                cache.update(&cacheSizeIndex, currentCacheSize);
                                cache.update(&newCacheEntryFlag, newCacheEntry);
                                cache.insert(&payloadByte, currentCacheSize);
                            }

                            return XDP_PASS;
                        }
                    }
                }
            }
        }
    }
    return XDP_PASS;
}
