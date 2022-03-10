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

struct data_response {
    int value;
    int port;
};

BPF_HISTOGRAM(counter, u64);
BPF_QUEUE(queue1, struct data_response, 10200);
BPF_QUEUE(queue2, struct data_response, 10200);
BPF_QUEUE(queue3, struct data_response, 10200);
BPF_QUEUE(queue4, struct data_response, 10200);
BPF_HASH(modify, int, struct data_response, 4);

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

                    u64 value = ntohs(udp->dest);
                    char *payload = data + sizeof(*eth) + sizeof(*ip) + sizeof(*udp);
                    if ( payload + 1 > data_end )
                        return XDP_PASS;
                    int val = 0;
                    struct data_response *response;
                    switch(value) {
                        case PORT_1 :
                            val = 1;
                            response = modify.lookup(&val);
                            if (response == NULL)
                                return XDP_PASS;
                            response->value = 1000000;
                            response->port = htons(udp->source);
                            queue1.push(response, 0);
                            break;
                        case PORT_2 :
                            val = 2;
                            response = modify.lookup(&val);
                            if (response == NULL)
                                return XDP_PASS;
                            response->value = 1000000;
                            response->port = htons(udp->source);
                            queue2.push(response, 0);
                            break;
                        case PORT_3 :
                            val = 3;
                            response = modify.lookup(&val);
                            if (response == NULL)
                                return XDP_PASS;
                            response->value = 1000000;
                            response->port = htons(udp->source);
                            queue3.push(response, 0);
                            break;
                        case PORT_4 :
                            val = 4;
                            response = modify.lookup(&val);
                            if (response == NULL)
                                return XDP_PASS;
                            response->value = 1000000;
                            response->port = htons(udp->source);
                            queue4.push(response, 0);
                            break;
                        default:
                            return XDP_PASS;
                            break;
                    }
                    counter.increment(value);
                    return XDP_DROP;
                }
            }
        }
    }
    return XDP_PASS;
}
