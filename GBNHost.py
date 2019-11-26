from Simulator import Simulator, Packet, EventEntity
from enum import Enum
from struct import pack, unpack


# In this class you will implement a full-duplex Go-Back-N client. Full-duplex means that this client can
# both send and receive data. You are responsible for implementing a Go-Back-N protocol in a simulated
# Transport layer. We are not going to use real network calls in this project, as we want to precisely
# simulate when packet delay, loss, and corruption occurs. As such, your simulated transport protocol
# will interface with the Simulator object to communicate with simulated Application and Network layers.
#
# The Simulator will call three functions that you are responsible for implementing. These functions define
# the interface by which the simulated Application and Network layers communicate with your transport layer:
# - receive_from_application_layer(payload) will be called when the Simulator has new data from the application
#   layer that needs to be sent across the network
# - receive_from_network_layer(byte_data) will be called when the Simulator has received a new packet from the
#   network layer that the transport layer needs to process
# - timer_interrupt() will be called when the Simulator detects that a timer has expired
#
# Your code can communicate with the Simulator by calling three methods:
# - Call self.simulator.to_layer5(payload) when your Transport layer has successfully received and processed
#   a data packet from the other host that needs to be delivered up to the Application layer
#    * to_layer5() expects to receive the payload of a packet as a decoded string, not as the bytes object
#      generated by unpack
# - Call self.simulator.to_layer3(byte_data) when your Transport layer has created a data packet or an ACK packet
#   that needs to be sent across the network to the other host
#    * to_layer3() expects to receive a packet that has been converted into a bytes object using pack. See the
#      next section in this comment for more detail
# - Call self.simulator.start_timer(self.entity, self.timer_interval) when you want to start a timer
#
# Additionally, you will need to write code to pack/unpack data into a byte representation appropriate for
# communication across a network. For this assignment, you will assume that all packets use the following header:
# - Sequence Number (int)           -- Set to 0 if this is an ACK
# - Acknowledgement Number (int)    -- Set to 0 if this is not an ACK
# - Checksum (half)                 -- Compute the Internet Checksum, as discussed in class
# - Acknowledgement Flag (boolean)  -- Set to True if sending an ACK, otherwise False
# - Payload length, in bytes (int)  -- Set this to 0 when sending an ACK message, as these will not carry a payload
# - Payload (string)                -- Leave this empty when sending an ACK message
# When unpacking data in this format, it is recommended to first unpack the fixed length header. After unpacking the
# header, you can determine if there is a payload, based on the size of Payload Length.
# NOTE: It is possible for payload length to be corrupted. In this case, you will get an Exception similar to
#       "unpack requires a buffer of ##### bytes". If you receive this exception, this is a sign that the packet is
#       corrupt. This is not the only way the packet can be corrupted, but is a special case of corruption that will
#       prevent you from unpacking the payload. If you can unpack the payload, use the checksum to determine if the
#       packet is corrupted. If you CAN'T unpack the payload, then you already KNOW that the packet is corrupted.
# When unpacking a packet, you can store the values in the Packet class, defined in the constructor. You MUST send
# data between hosts in a byte representation, but after receiving a packet you may find it convenient to
# store the values in this class, as it will allow you to refer to them by name in your code, rather than via
# the array indicies produced by unpack().
#
# Finally, you will need to implement the Internet Checksum algorithm for your packets. As discussed in class,
# sum each of the 16-bit words of the packet, carrying around any overflow bits. Once you have summed all of the
# 16-bit words, perform the 1's complement. If a packet contains an odd number of bytes (i.e. the last byte doesn't
# fit into a 16-bit word), pad the packet (when computing the checksum) with a 0 byte. When receiving a packet,
# check that it is valid using this checksum.
#
# NOTE: By default, all of the test cases created for this program capture print() output and save it in a log
#       file with the same name as the test case being run. You can disable this functionality by editing
#       the test***.cfg file and removing the --capture_log argument (just delete it). Do NOT change any other
#       of the option parameters in test***.cfg

class GBNHost():

    # The __init__ method accepts:
    # - a reference to the simulator object
    # - the name for this entity (EntityType.A or EntityType.B)
    # - the interval for this entity's timer
    # - the size of the window used for the Go-Back-N algorithm
    def __init__(self, simulator, entity, timer_interval, window_size):

        # These are important state values that you will need to use in your code
        self.simulator = simulator
        self.entity = entity

        # Sender properties
        # The duration the timer lasts before triggering
        self.timer_interval = timer_interval
        self.window_size = window_size              # The size of the seq/ack window
        # The last ACKed packet. This starts at 0 because no packets
        self.last_ACKed = 0
        # have been ACKed
        # The SEQ number that will be used next
        self.current_seq_number = 1
        # A buffer that stores all data received from the application
        self.app_layer_buffer = []
        # layer that hasn't yet been sent
        # A buffer that stores all sent but unACKed packets
        self.unACKed_buffer = {}

        # Receiver properties
        self.expected_seq_number = 1                # The next SEQ number expected
        # The last ACK pkt sent.
        self.last_ACK_pkt = self.make_pkt(
            self.current_seq_number, 0, True, 0)
        # TODO: This should be initialized to an ACK response with an
        #       ACK number of 0. If a problem occurs with the first
        #       packet that is received, then this default ACK should
        #       be sent in response, as no real packet has been rcvd yet

    ###########################################################################################################
    # Core Interface functions that are called by Simulator

    # This function implements the SENDING functionality. It should implement retransmit-on-timeout.
    # Refer to the GBN sender flowchart for details about how this function should be implemented
    # NOTE: DIFFERENCE FROM GBN FLOWCHART
    #       If this function receives data to send while it does NOT have an open slot in the sending window,
    #       it should store this data in self.app_layer_buffer. This data should be immediately sent
    #       when slots open up in the sending window.
    # TODO: Implement this method

    def receive_from_application_layer(self, payload):
        sndpkt = bytearray
        # arb_checksum = 1
        if self.current_seq_number < (self.last_ACKed + self.window_size):
            sndpkt = self.make_pkt(self.current_seq_number, 0, False, len(
                payload), payload.encode(), None)
            checksum = self.checksum(sndpkt)
            # print("This is the send pkt: ", sndpkt)
            sndpkt = self.make_pkt(self.current_seq_number, 0, False, len(
                payload), payload.encode(), checksum)
            self.simulator.to_layer3(self.entity, sndpkt, False)
            self.unACKed_buffer[self.current_seq_number] = sndpkt


            if self.last_ACKed == self.current_seq_number:
                print("last = curr")
                self.simulator.start_timer(self.entity, self.timer_interval)
            self.current_seq_number += 1
        else:
            self.app_layer_buffer.append(sndpkt)
        


    # This function implements the RECEIVING functionality. This function will be more complex than
    # receive_from_application_layer(), as it must process both packets containing new data, and packets
    # containing ACKs. You will need to handle received data differently depending on if it is an ACK
    # or a packet containing data.
    # Refer to the GBN receiver flowchart for details about how to implement responding to data pkts, and
    # refer to the GBN sender flowchart for details about how to implement responidng to ACKs
    # NOTE: DIFFERENCE FROM GBN FLOWCHART
    #       If the received packet is corrupt, you should always resend the last sent ACK. If the packet
    #       is corrupt, we can't be certain if it was an ACK or a packet containing data. In the flowchart
    #       we do nothing if the corrupted packet was an ACK, but we re-send the last ACK if the corrupted
    #       packet had data. Re-sending an extra ACK won't cause any problems, so we'd rather do that than
    #       not send an ACK when we should have
    # TODO: Implement this method

    def receive_from_network_layer(self, byte_data):

       
        if self.corrupted(byte_data):
            print("This pkt is corrupt")
            self.simulator.to_layer3(self.entity, self.last_ACK_pkt, True)
        else:
            
            # print("Pkt is not corrupted: ")
            header = unpack('!iiH?i', byte_data[0:15])

            payload_length = header[4]
            if payload_length > 0:
                unpacked_pkt = unpack('!iiH?i%is' % payload_length, byte_data)
                self.simulator.to_layer5(self.entity, unpacked_pkt[5].decode())
                print("Sent data: ", unpacked_pkt[5].decode())
                ackpkt = self.make_pkt(self.expected_seq_number, self.current_seq_number, True, 0)
                self.simulator.to_layer3(self.entity, ackpkt, True)
                self.last_ACK_pkt = ackpkt
                self.expected_seq_number += 1
            else:
                print("ack has been received")
                self.last_ACKed = header[1] + 1
                if self.last_ACKed == self.current_seq_number:
                    self.simulator.stop_timer(self.entity)
                else:
                    self.simulator.start_timer(self.entity, self.timer_interval)


    # This function is called by the simulator when a timer interrupt is triggered due to an ACK not being
    # received in the expected time frame. All unACKed data should be resent, and the timer restarted
    # TODO: Implement this method

    def timer_interrupt(self):
        for x in self.unACKed_buffer.values():
            self.simulator.to_layer3(self.entity, x, False)
        self.simulator.start_timer(self.entity, self.timer_interval)

    def make_pkt(self, seq_num, ack, is_ack, payload_len, payload=None, checksum=None):
        sndpkt = bytearray
        if payload != None and checksum == None:  # preprocessing for computing checksum
            sndpkt = pack('!ii?i%is' % payload_len, seq_num,
                          ack, is_ack, payload_len, payload)
            return sndpkt

        elif payload != None and checksum != None:  # full data pkt with checksum included
            sndpkt = pack('!iiH?i%is' % payload_len, seq_num, ack,
                          checksum, is_ack, payload_len, payload)
            return sndpkt

        else:# ACK pkt with payload length set to 0 and empty payload
            sndpkt = pack('!ii?i', seq_num, ack, is_ack, payload_len)
            checksum = self.checksum(sndpkt)
            sndpkt = pack('!iiH?i', seq_num, ack, checksum, is_ack, payload_len)
            print("ACK pkt has been created")
            return sndpkt

    def checksum(self, packet):
        s = 0x0000

        # If we have an odd number of bytes, pad the packet with 0x0000
        padded_pkt = None
        if len(packet) % 2 == 1:
            padded_pkt = packet + bytes(1)
        else:
            padded_pkt = packet

        for i in range(0, len(padded_pkt), 2):
            w = padded_pkt[i] << 8 | padded_pkt[i+1]
            s = self.carry_around_add(s, w)
        return ~s & 0xffff

    def carry_around_add(self, a, b):
        c = a + b
        return (c & 0xffff) + (c >> 16)

    def corrupted(self, sndpkt):
        print("Checksum in corrupted = ", self.checksum(sndpkt))
        if self.checksum(sndpkt) == 0x0000:
            return False
        else:
            return True
