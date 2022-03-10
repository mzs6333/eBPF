// Matthew Sickler 2022

#define KBUILD_MODNAME "udp_demultiplex"
#include <linux/bpf.h>
#include <linux/if_ether.h>
#include <linux/ip.h>
#include <linux/udp.h>
#include <linux/in.h>
#include <linux/if_packet.h>
#include <linux/if_vlan.h>
#include <linux/types.h>

#define PORT_1 51141
#define PORT_2 51142
#define PORT_3 51143
#define PORT_4 51144
#define MAX_UDP_LENGTH 1480
#define PAYLOAD_SIZE 7

BPF_HISTOGRAM(counter, u64);

int udp_demultiplex(struct xdp_md *ctx)
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
                    char *payload = data + sizeof(*eth) + sizeof(*ip) + sizeof(*udp);
                    if ( payload + 1 > data_end )
                        return XDP_PASS;
                    char payloadString[PAYLOAD_SIZE+1];
                    int payloadValueInt = 0;
                    switch(value) {
                        case PORT_1 :
                            memcpy(payloadString, (char *)payload, PAYLOAD_SIZE);
                            for(int i=0; i < 1400; i++) {
                                int temp = payloadValueInt;
                                temp++;
                                payloadValueInt = temp;
                            }
                            break;
                        case PORT_2 :
                            memcpy(payloadString, (char *)payload, PAYLOAD_SIZE);
                            for(int i=0; i < 1000; i++) {
                                int temp = payloadValueInt;
                                temp++;
                                payloadValueInt = temp;
                            }
                            break;
                        case PORT_3 :
                            memcpy(payloadString, (char *)payload, PAYLOAD_SIZE);
                            for(int i=0; i < 10; i++) {
                                int temp = payloadValueInt;
                                temp++;
                                payloadValueInt = temp;
                            }
                            break;
                        case PORT_4 :
                            memcpy(payloadString, (char *)payload, PAYLOAD_SIZE);
                            for(int i=0; i < 500; i++) {
                                int temp = payloadValueInt;
                                temp++;
                                payloadValueInt = temp;
                            }
                            break;
                        default:
                            return XDP_PASS;
                            break;
                    }
                    counter.increment(value);
                    
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
            }
        }
    }
    return XDP_PASS;
}
