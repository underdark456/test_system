from src.drivers.snmp.abstract_uhp_snmp import AbstractUhpSnmp
from src.drivers.snmp.basic_objects import _Node, _ReadWriteLeaf, _ReadLeaf

"""This code is generated automatically. Consult a psychiatrist before changing.
See utilities/mib_convertor/"""


class _System(_Node):

    def sys_descr(self, item_number=0) -> _ReadLeaf:
        """A textual description of the entity.  This value
should include the full name and version
identification of the system's hardware type,
software operating-system, and networking
software.  It is mandatory that this only contain
printable ASCII characters."""
        self._oid = '1.3.6.1.2.1.1.1' + '.' + str(item_number)
        return _ReadLeaf(self._get)

    def sys_object_id(self, item_number=0) -> _ReadLeaf:
        """The vendor's authoritative identification of the
network management subsystem contained in the
entity.  This value is allocated within the SMI
enterprises subtree (1.3.6.1.4.1) and provides an
easy and unambiguous means for determining `what
kind of box' is being managed.  For example, if
vendor `Flintstones, Inc.' was assigned the
subtree 1.3.6.1.4.1.4242, it could assign the
identifier 1.3.6.1.4.1.4242.1.1 to its `Fred
Router'."""
        self._oid = '1.3.6.1.2.1.1.2' + '.' + str(item_number)
        return _ReadLeaf(self._get)

    def sys_up_time(self, item_number=0) -> _ReadLeaf:
        """The time (in hundredths of a second) since the
network management portion of the system was last
re-initialized."""
        self._oid = '1.3.6.1.2.1.1.3' + '.' + str(item_number)
        return _ReadLeaf(self._get)

    def sys_contact(self, item_number=0) -> _ReadWriteLeaf:
        """The textual identification of the contact person
for this managed node, together with information
on how to contact this person."""
        self._oid = '1.3.6.1.2.1.1.4' + '.' + str(item_number)
        return _ReadWriteLeaf(self._get, self._set)

    def sys_name(self, item_number=0) -> _ReadWriteLeaf:
        """An administratively-assigned name for this
managed node.  By convention, this is the node's
fully-qualified domain name."""
        self._oid = '1.3.6.1.2.1.1.5' + '.' + str(item_number)
        return _ReadWriteLeaf(self._get, self._set)

    def sys_location(self, item_number=0) -> _ReadWriteLeaf:
        """The physical location of this node (e.g.,
`telephone closet, 3rd floor')."""
        self._oid = '1.3.6.1.2.1.1.6' + '.' + str(item_number)
        return _ReadWriteLeaf(self._get, self._set)

    def sys_services(self, item_number=0) -> _ReadLeaf:
        """A value which indicates the set of services that
this entity primarily offers.

The value is a sum.  This sum initially takes the
value zero, Then, for each layer, L, in the range
1 through 7, that this node performs transactions
for, 2 raised to (L - 1) is added to the sum.  For
example, a node which performs primarily routing
functions would have a value of 4 (2^(3-1)).  In
contrast, a node which is a host offering
application services would have a value of 72
(2^(4-1) + 2^(7-1)).  Note that in the context of
the Internet suite of protocols, values should be
calculated accordingly:

     layer  functionality
         1  physical (e.g., repeaters)
         2  datalink/subnetwork (e.g., bridges)
         3  internet (e.g., IP gateways)
         4  end-to-end  (e.g., IP hosts)
         7  applications (e.g., mail relays)

For systems including OSI protocols, layers 5 and
6 may also be counted."""
        self._oid = '1.3.6.1.2.1.1.7' + '.' + str(item_number)
        return _ReadLeaf(self._get)

    def sys_or_last(self, item_number=0) -> _ReadLeaf:
        """"""
        self._oid = '1.3.6.1.2.1.1.8' + '.' + str(item_number)
        return _ReadLeaf(self._get)


class _Interfaces(_Node):

    def if_number(self, item_number=0) -> _ReadLeaf:
        """The number of network interfaces (regardless of
their current state) present on this system."""
        self._oid = '1.3.6.1.2.1.2.1' + '.' + str(item_number)
        return _ReadLeaf(self._get)

    def if_descr(self, item_number=0) -> _ReadLeaf:
        """A textual string containing information about the
interface.  This string should include the name of
the manufacturer, the product name and the version
of the hardware interface."""
        self._oid = '1.3.6.1.2.1.2.2.1.2' + '.' + str(item_number)
        return _ReadLeaf(self._get)

    def if_type(self, item_number=0) -> _ReadLeaf:
        """The type of interface, distinguished according to
the physical/link protocol(s) immediately `below'
the network layer in the protocol stack."""
        self._oid = '1.3.6.1.2.1.2.2.1.3' + '.' + str(item_number)
        return _ReadLeaf(self._get)

    def if_mtu(self, item_number=0) -> _ReadLeaf:
        """The size of the largest datagram which can be
sent/received on the interface, specified in
octets.  For interfaces that are used for
transmitting network datagrams, this is the size
of the largest network datagram that can be sent
on the interface."""
        self._oid = '1.3.6.1.2.1.2.2.1.4' + '.' + str(item_number)
        return _ReadLeaf(self._get)

    def if_speed(self, item_number=0) -> _ReadLeaf:
        """An estimate of the interface's current bandwidth
in bits per second.  For interfaces which do not
vary in bandwidth or for those where no accurate
estimation can be made, this object should contain
the nominal bandwidth."""
        self._oid = '1.3.6.1.2.1.2.2.1.5' + '.' + str(item_number)
        return _ReadLeaf(self._get)

    def if_phys_address(self, item_number=0) -> _ReadLeaf:
        """The interface's address at the protocol layer
immediately `below' the network layer in the
protocol stack.  For interfaces which do not have
such an address (e.g., a serial line), this object
should contain an octet string of zero length."""
        self._oid = '1.3.6.1.2.1.2.2.1.6' + '.' + str(item_number)
        return _ReadLeaf(self._get)

    def if_admin_status(self, item_number=0) -> _ReadWriteLeaf:
        """The desired state of the interface.  The
testing(3) state indicates that no operational
packets can be passed."""
        self._oid = '1.3.6.1.2.1.2.2.1.7' + '.' + str(item_number)
        return _ReadWriteLeaf(self._get, self._set)

    def if_oper_status(self, item_number=0) -> _ReadLeaf:
        """The current operational state of the interface.
The testing(3) state indicates that no operational
packets can be passed."""
        self._oid = '1.3.6.1.2.1.2.2.1.8' + '.' + str(item_number)
        return _ReadLeaf(self._get)

    def if_last_change(self, item_number=0) -> _ReadLeaf:
        """The value of sysUpTime at the time the interface
entered its current operational state.  If the
current state was entered prior to the last re-
initialization of the local network management
subsystem, then this object contains a zero
value."""
        self._oid = '1.3.6.1.2.1.2.2.1.9' + '.' + str(item_number)
        return _ReadLeaf(self._get)

    def if_in_octets(self, item_number=0) -> _ReadLeaf:
        """The total number of octets received on the
interface, including framing characters."""
        self._oid = '1.3.6.1.2.1.2.2.1.10' + '.' + str(item_number)
        return _ReadLeaf(self._get)

    def if_in_ucast_pkts(self, item_number=0) -> _ReadLeaf:
        """The number of subnetwork-unicast packets
delivered to a higher-layer protocol."""
        self._oid = '1.3.6.1.2.1.2.2.1.11' + '.' + str(item_number)
        return _ReadLeaf(self._get)

    def if_in_n_ucast_pkts(self, item_number=0) -> _ReadLeaf:
        """The number of non-unicast (i.e., subnetwork-
broadcast or subnetwork-multicast) packets
delivered to a higher-layer protocol."""
        self._oid = '1.3.6.1.2.1.2.2.1.12' + '.' + str(item_number)
        return _ReadLeaf(self._get)

    def if_in_discards(self, item_number=0) -> _ReadLeaf:
        """The number of inbound packets which were chosen
to be discarded even though no errors had been
detected to prevent their being deliverable to a
higher-layer protocol.  One possible reason for
discarding such a packet could be to free up
buffer space."""
        self._oid = '1.3.6.1.2.1.2.2.1.13' + '.' + str(item_number)
        return _ReadLeaf(self._get)

    def if_in_errors(self, item_number=0) -> _ReadLeaf:
        """The number of inbound packets that contained
errors preventing them from being deliverable to a
higher-layer protocol."""
        self._oid = '1.3.6.1.2.1.2.2.1.14' + '.' + str(item_number)
        return _ReadLeaf(self._get)

    def if_in_unknown_protos(self, item_number=0) -> _ReadLeaf:
        """The number of packets received via the interface
which were discarded because of an unknown or
unsupported protocol."""
        self._oid = '1.3.6.1.2.1.2.2.1.15' + '.' + str(item_number)
        return _ReadLeaf(self._get)

    def if_out_octets(self, item_number=0) -> _ReadLeaf:
        """The total number of octets transmitted out of the
interface, including framing characters."""
        self._oid = '1.3.6.1.2.1.2.2.1.16' + '.' + str(item_number)
        return _ReadLeaf(self._get)

    def if_out_ucast_pkts(self, item_number=0) -> _ReadLeaf:
        """The total number of packets that higher-level
protocols requested be transmitted to a
subnetwork-unicast address, including those that
were discarded or not sent."""
        self._oid = '1.3.6.1.2.1.2.2.1.17' + '.' + str(item_number)
        return _ReadLeaf(self._get)

    def if_out_n_ucast_pkts(self, item_number=0) -> _ReadLeaf:
        """The total number of packets that higher-level
protocols requested be transmitted to a non-
unicast (i.e., a subnetwork-broadcast or
subnetwork-multicast) address, including those
that were discarded or not sent."""
        self._oid = '1.3.6.1.2.1.2.2.1.18' + '.' + str(item_number)
        return _ReadLeaf(self._get)

    def if_out_discards(self, item_number=0) -> _ReadLeaf:
        """The number of outbound packets which were chosen
to be discarded even though no errors had been
detected to prevent their being transmitted.  One
possible reason for discarding such a packet could
be to free up buffer space."""
        self._oid = '1.3.6.1.2.1.2.2.1.19' + '.' + str(item_number)
        return _ReadLeaf(self._get)

    def if_out_errors(self, item_number=0) -> _ReadLeaf:
        """The number of outbound packets that could not be
transmitted because of errors."""
        self._oid = '1.3.6.1.2.1.2.2.1.20' + '.' + str(item_number)
        return _ReadLeaf(self._get)

    def if_out_q_len(self, item_number=0) -> _ReadLeaf:
        """The length of the output packet queue (in
packets)."""
        self._oid = '1.3.6.1.2.1.2.2.1.21' + '.' + str(item_number)
        return _ReadLeaf(self._get)

    def if_specific(self, item_number=0) -> _ReadLeaf:
        """A reference to MIB definitions specific to the
particular media being used to realize the
interface.  For example, if the interface is
realized by an ethernet, then the value of this
object refers to a document defining objects
specific to ethernet.  If this information is not
present, its value should be set to the OBJECT
IDENTIFIER { 0 0 }, which is a syntatically valid
object identifier, and any conformant
implementation of ASN.1 and BER must be able to
generate and recognize this value."""
        self._oid = '1.3.6.1.2.1.2.2.1.22' + '.' + str(item_number)
        return _ReadLeaf(self._get)


class _Mib2(_Node):

    def system(self) -> _System:
        return _System(self._parent_call)

    def interfaces(self) -> _Interfaces:
        return _Interfaces(self._parent_call)


class _Control(_Node):

    def save_config(self, item_number=0) -> _ReadWriteLeaf:
        """Save current profile to EEPROM profile 0-2.
Profile 0 is automativally loaded on restart by default."""
        self._oid = '1.3.6.1.4.1.8000.22.1.1' + '.' + str(item_number)
        return _ReadWriteLeaf(self._get, self._set)

    def reboot(self, item_number=0) -> _ReadWriteLeaf:
        """Reboot device immediately."""
        self._oid = '1.3.6.1.4.1.8000.22.1.2' + '.' + str(item_number)
        return _ReadWriteLeaf(self._get, self._set)

    def command(self, item_number=0) -> _ReadWriteLeaf:
        """Issue a command to command-line interface."""
        self._oid = '1.3.6.1.4.1.8000.22.1.3' + '.' + str(item_number)
        return _ReadWriteLeaf(self._get, self._set)

    def config_edit(self, item_number=0) -> _ReadWriteLeaf:
        """Profile or global config editing and viewing
Complex input format, only for manufacturer."""
        self._oid = '1.3.6.1.4.1.8000.22.1.4' + '.' + str(item_number)
        return _ReadWriteLeaf(self._get, self._set)

    def profile(self, item_number=0) -> _ReadWriteLeaf:
        """Get current profile or run specified profile (1-8)."""
        self._oid = '1.3.6.1.4.1.8000.22.1.5' + '.' + str(item_number)
        return _ReadWriteLeaf(self._get, self._set)


class _Demod1(_Node):

    def lband_s_n_r1(self, item_number=0) -> _ReadLeaf:
        """Signal to noise ratio at L-band demodulator input
measured in 0.1 dB units."""
        self._oid = '1.3.6.1.4.1.8000.22.2.1' + '.' + str(item_number)
        return _ReadLeaf(self._get)

    def lband_offset1(self, item_number=0) -> _ReadLeaf:
        """Frequency offset value in KHz between PLL frequency and
carrier real frequency."""
        self._oid = '1.3.6.1.4.1.8000.22.2.2' + '.' + str(item_number)
        return _ReadLeaf(self._get)

    def in_lvl1(self, item_number=0) -> _ReadLeaf:
        """Current input level x -10dBm"""
        self._oid = '1.3.6.1.4.1.8000.22.2.3' + '.' + str(item_number)
        return _ReadLeaf(self._get)

    def in_bytes1(self, item_number=0) -> _ReadLeaf:
        """Demodulator1 traffic in bytes
(indexed by ACM channel)"""
        self._oid = '1.3.6.1.4.1.8000.22.2.4' + '.' + str(item_number)
        return _ReadLeaf(self._get)


class _Demod2(_Node):

    def lband_s_n_r2(self, item_number=0) -> _ReadLeaf:
        """Signal to noise ratio at L-band demodulator input
measured in 0.1 dB units."""
        self._oid = '1.3.6.1.4.1.8000.22.3.1' + '.' + str(item_number)
        return _ReadLeaf(self._get)

    def lband_offset2(self, item_number=0) -> _ReadLeaf:
        """Frequency offset value in KHz between PLL frequency and
carrier real frequency."""
        self._oid = '1.3.6.1.4.1.8000.22.3.2' + '.' + str(item_number)
        return _ReadLeaf(self._get)

    def in_lvl2(self, item_number=0) -> _ReadLeaf:
        """Current input level x -10dBm"""
        self._oid = '1.3.6.1.4.1.8000.22.3.3' + '.' + str(item_number)
        return _ReadLeaf(self._get)

    def in_bytes2(self, item_number=0) -> _ReadLeaf:
        """Demodulator2 traffic in bytes
(indexed by ACM channel)"""
        self._oid = '1.3.6.1.4.1.8000.22.3.4' + '.' + str(item_number)
        return _ReadLeaf(self._get)


class _PrioAll(_Node):

    def out_bytes_a(self, item_number=0) -> _ReadLeaf:
        """Modulator traffic in bytes
(indexed by ACM channel)"""
        self._oid = '1.3.6.1.4.1.8000.22.4.1.1' + '.' + str(item_number)
        return _ReadLeaf(self._get)

    def out_pkts_a(self, item_number=0) -> _ReadLeaf:
        """Modulator traffic in packets
(indexed by ACM channel)"""
        self._oid = '1.3.6.1.4.1.8000.22.4.1.2' + '.' + str(item_number)
        return _ReadLeaf(self._get)

    def drops_a(self, item_number=0) -> _ReadLeaf:
        """Modulator dropped packets
(indexed by ACM channel)"""
        self._oid = '1.3.6.1.4.1.8000.22.4.1.3' + '.' + str(item_number)
        return _ReadLeaf(self._get)

    def queue_len_b_a(self, item_number=0) -> _ReadLeaf:
        """Modulator queue length in bytes
(indexed by ACM channel)"""
        self._oid = '1.3.6.1.4.1.8000.22.4.1.4' + '.' + str(item_number)
        return _ReadLeaf(self._get)

    def queue_len_p_a(self, item_number=0) -> _ReadLeaf:
        """Modulator queue length in packets
(indexed by ACM channel)"""
        self._oid = '1.3.6.1.4.1.8000.22.4.1.5' + '.' + str(item_number)
        return _ReadLeaf(self._get)

    def num_stations(self, item_number=0) -> _ReadLeaf:
        """Number of stations per ACM channel
(indexed by ACM channel)"""
        self._oid = '1.3.6.1.4.1.8000.22.4.1.6' + '.' + str(item_number)
        return _ReadLeaf(self._get)


class _PrioP1(_Node):

    def out_bytes_p1(self, item_number=0) -> _ReadLeaf:
        """Modulator P1(Low) priority traffic in bytes
(indexed by ACM channel)"""
        self._oid = '1.3.6.1.4.1.8000.22.4.2.1' + '.' + str(item_number)
        return _ReadLeaf(self._get)

    def out_pkts_p1(self, item_number=0) -> _ReadLeaf:
        """Modulator P1(Low) priority traffic in packets
(indexed by ACM channel)"""
        self._oid = '1.3.6.1.4.1.8000.22.4.2.2' + '.' + str(item_number)
        return _ReadLeaf(self._get)

    def drops_p1(self, item_number=0) -> _ReadLeaf:
        """Modulator P1(Low) priority dropped packets
(indexed by ACM channel)"""
        self._oid = '1.3.6.1.4.1.8000.22.4.2.3' + '.' + str(item_number)
        return _ReadLeaf(self._get)

    def queue_len_b_p1(self, item_number=0) -> _ReadLeaf:
        """Modulator P1(Low) priority queue length in bytes
(indexed by ACM channel)"""
        self._oid = '1.3.6.1.4.1.8000.22.4.2.4' + '.' + str(item_number)
        return _ReadLeaf(self._get)

    def queue_len_p_p1(self, item_number=0) -> _ReadLeaf:
        """Modulator P1(Low) priority queue length in packets
(indexed by ACM channel)"""
        self._oid = '1.3.6.1.4.1.8000.22.4.2.5' + '.' + str(item_number)
        return _ReadLeaf(self._get)


class _PrioP4(_Node):

    def out_bytes_p4(self, item_number=0) -> _ReadLeaf:
        """Modulator P4(Med) priority traffic in bytes 
(indexed by ACM channel)"""
        self._oid = '1.3.6.1.4.1.8000.22.4.3.1' + '.' + str(item_number)
        return _ReadLeaf(self._get)

    def out_pkts_p4(self, item_number=0) -> _ReadLeaf:
        """Modulator P4(Med) priority traffic in packets
(indexed by ACM channel)"""
        self._oid = '1.3.6.1.4.1.8000.22.4.3.2' + '.' + str(item_number)
        return _ReadLeaf(self._get)

    def drops_p4(self, item_number=0) -> _ReadLeaf:
        """Modulator P4(Med) priority dropped packets
(indexed by ACM channel)"""
        self._oid = '1.3.6.1.4.1.8000.22.4.3.3' + '.' + str(item_number)
        return _ReadLeaf(self._get)

    def queue_len_b_p4(self, item_number=0) -> _ReadLeaf:
        """Modulator P4(Med) priority queue length in bytes
(indexed by ACM channel)"""
        self._oid = '1.3.6.1.4.1.8000.22.4.3.4' + '.' + str(item_number)
        return _ReadLeaf(self._get)

    def queue_len_p_p4(self, item_number=0) -> _ReadLeaf:
        """Modulator P4(Med) priority queue length in packets
(indexed by ACM channel)"""
        self._oid = '1.3.6.1.4.1.8000.22.4.3.5' + '.' + str(item_number)
        return _ReadLeaf(self._get)


class _PrioP7(_Node):

    def out_bytes_p7(self, item_number=0) -> _ReadLeaf:
        """Modulator P7(High) priority traffic in bytes
(indexed by ACM channel)"""
        self._oid = '1.3.6.1.4.1.8000.22.4.4.1' + '.' + str(item_number)
        return _ReadLeaf(self._get)

    def out_pkts_p7(self, item_number=0) -> _ReadLeaf:
        """Modulator P7(High) priority traffic in packets
(indexed by ACM channel)"""
        self._oid = '1.3.6.1.4.1.8000.22.4.4.2' + '.' + str(item_number)
        return _ReadLeaf(self._get)

    def drops_p7(self, item_number=0) -> _ReadLeaf:
        """Modulator P7(High) priority dropped packets
(indexed by ACM channel)"""
        self._oid = '1.3.6.1.4.1.8000.22.4.4.3' + '.' + str(item_number)
        return _ReadLeaf(self._get)

    def queue_len_b_p7(self, item_number=0) -> _ReadLeaf:
        """Modulator P7(High) priority queue length in bytes
(indexed by ACM channel)"""
        self._oid = '1.3.6.1.4.1.8000.22.4.4.4' + '.' + str(item_number)
        return _ReadLeaf(self._get)

    def queue_len_p_p7(self, item_number=0) -> _ReadLeaf:
        """Modulator P7(High) priority queue length in packets
(indexed by ACM channel)"""
        self._oid = '1.3.6.1.4.1.8000.22.4.4.5' + '.' + str(item_number)
        return _ReadLeaf(self._get)


class _PrioCtrl(_Node):

    def out_bytes_c(self, item_number=0) -> _ReadLeaf:
        """Modulator control traffic in bytes
(index 1 only)"""
        self._oid = '1.3.6.1.4.1.8000.22.4.5.1' + '.' + str(item_number)
        return _ReadLeaf(self._get)

    def out_pkts_c(self, item_number=0) -> _ReadLeaf:
        """Modulator control traffic in packets
(index 1 only)"""
        self._oid = '1.3.6.1.4.1.8000.22.4.5.2' + '.' + str(item_number)
        return _ReadLeaf(self._get)


class _Level(_Node):

    def tx_level(self, item_number=0) -> _ReadLeaf:
        """Current TX level x -10dBm"""
        self._oid = '1.3.6.1.4.1.8000.22.4.6.1' + '.' + str(item_number)
        return _ReadLeaf(self._get)

    def tx_level_delta(self, item_number=0) -> _ReadLeaf:
        """Current TX level delta from set level x -10dBm"""
        self._oid = '1.3.6.1.4.1.8000.22.4.6.2' + '.' + str(item_number)
        return _ReadLeaf(self._get)

    def tx_max_level(self, item_number=0) -> _ReadLeaf:
        """Max TLC level x -10dBm"""
        self._oid = '1.3.6.1.4.1.8000.22.4.6.3' + '.' + str(item_number)
        return _ReadLeaf(self._get)


class _PrioP2(_Node):

    def out_bytes_p2(self, item_number=0) -> _ReadLeaf:
        """Modulator P2 priority traffic in bytes
(indexed by ACM channel)"""
        self._oid = '1.3.6.1.4.1.8000.22.4.7.1' + '.' + str(item_number)
        return _ReadLeaf(self._get)

    def out_pkts_p2(self, item_number=0) -> _ReadLeaf:
        """Modulator P2 priority traffic in packets
(indexed by ACM channel)"""
        self._oid = '1.3.6.1.4.1.8000.22.4.7.2' + '.' + str(item_number)
        return _ReadLeaf(self._get)

    def drops_p2(self, item_number=0) -> _ReadLeaf:
        """Modulator P2 priority dropped packets
(indexed by ACM channel)"""
        self._oid = '1.3.6.1.4.1.8000.22.4.7.3' + '.' + str(item_number)
        return _ReadLeaf(self._get)

    def queue_len_b_p2(self, item_number=0) -> _ReadLeaf:
        """Modulator P2 priority queue length in bytes
(indexed by ACM channel)"""
        self._oid = '1.3.6.1.4.1.8000.22.4.7.4' + '.' + str(item_number)
        return _ReadLeaf(self._get)

    def queue_len_p_p2(self, item_number=0) -> _ReadLeaf:
        """Modulator P2 priority queue length in packets
(indexed by ACM channel)"""
        self._oid = '1.3.6.1.4.1.8000.22.4.7.5' + '.' + str(item_number)
        return _ReadLeaf(self._get)


class _PrioP3(_Node):

    def out_bytes_p3(self, item_number=0) -> _ReadLeaf:
        """Modulator P3 priority traffic in bytes
(indexed by ACM channel)"""
        self._oid = '1.3.6.1.4.1.8000.22.4.8.1' + '.' + str(item_number)
        return _ReadLeaf(self._get)

    def out_pkts_p3(self, item_number=0) -> _ReadLeaf:
        """Modulator P3 priority traffic in packets
(indexed by ACM channel)"""
        self._oid = '1.3.6.1.4.1.8000.22.4.8.2' + '.' + str(item_number)
        return _ReadLeaf(self._get)

    def drops_p3(self, item_number=0) -> _ReadLeaf:
        """Modulator P3 priority dropped packets
(indexed by ACM channel)"""
        self._oid = '1.3.6.1.4.1.8000.22.4.8.3' + '.' + str(item_number)
        return _ReadLeaf(self._get)

    def queue_len_b_p3(self, item_number=0) -> _ReadLeaf:
        """Modulator P3 priority queue length in bytes
(indexed by ACM channel)"""
        self._oid = '1.3.6.1.4.1.8000.22.4.8.4' + '.' + str(item_number)
        return _ReadLeaf(self._get)

    def queue_len_p_p3(self, item_number=0) -> _ReadLeaf:
        """Modulator P3 priority queue length in packets
(indexed by ACM channel)"""
        self._oid = '1.3.6.1.4.1.8000.22.4.8.5' + '.' + str(item_number)
        return _ReadLeaf(self._get)


class _PrioP5(_Node):

    def out_bytes_p5(self, item_number=0) -> _ReadLeaf:
        """Modulator P5 priority traffic in bytes
(indexed by ACM channel)"""
        self._oid = '1.3.6.1.4.1.8000.22.4.9.1' + '.' + str(item_number)
        return _ReadLeaf(self._get)

    def out_pkts_p5(self, item_number=0) -> _ReadLeaf:
        """Modulator P5 priority traffic in packets
(indexed by ACM channel)"""
        self._oid = '1.3.6.1.4.1.8000.22.4.9.2' + '.' + str(item_number)
        return _ReadLeaf(self._get)

    def drops_p5(self, item_number=0) -> _ReadLeaf:
        """Modulator P5 priority dropped packets
(indexed by ACM channel)"""
        self._oid = '1.3.6.1.4.1.8000.22.4.9.3' + '.' + str(item_number)
        return _ReadLeaf(self._get)

    def queue_len_b_p5(self, item_number=0) -> _ReadLeaf:
        """Modulator P5 priority queue length in bytes
(indexed by ACM channel)"""
        self._oid = '1.3.6.1.4.1.8000.22.4.9.4' + '.' + str(item_number)
        return _ReadLeaf(self._get)

    def queue_len_p_p5(self, item_number=0) -> _ReadLeaf:
        """Modulator P5 priority queue length in packets
(indexed by ACM channel)"""
        self._oid = '1.3.6.1.4.1.8000.22.4.9.5' + '.' + str(item_number)
        return _ReadLeaf(self._get)


class _PrioP6(_Node):

    def out_bytes_p6(self, item_number=0) -> _ReadLeaf:
        """Modulator P6 priority traffic in bytes
(indexed by ACM channel)"""
        self._oid = '1.3.6.1.4.1.8000.22.4.10.1' + '.' + str(item_number)
        return _ReadLeaf(self._get)

    def out_pkts_p6(self, item_number=0) -> _ReadLeaf:
        """Modulator P6 priority traffic in packets
(indexed by ACM channel)"""
        self._oid = '1.3.6.1.4.1.8000.22.4.10.2' + '.' + str(item_number)
        return _ReadLeaf(self._get)

    def drops_p6(self, item_number=0) -> _ReadLeaf:
        """Modulator P6 priority dropped packets
(indexed by ACM channel)"""
        self._oid = '1.3.6.1.4.1.8000.22.4.10.3' + '.' + str(item_number)
        return _ReadLeaf(self._get)

    def queue_len_b_p6(self, item_number=0) -> _ReadLeaf:
        """Modulator P6 priority queue length in bytes
(indexed by ACM channel)"""
        self._oid = '1.3.6.1.4.1.8000.22.4.10.4' + '.' + str(item_number)
        return _ReadLeaf(self._get)

    def queue_len_p_p6(self, item_number=0) -> _ReadLeaf:
        """Modulator P6 priority queue length in packets
(indexed by ACM channel)"""
        self._oid = '1.3.6.1.4.1.8000.22.4.10.5' + '.' + str(item_number)
        return _ReadLeaf(self._get)


class _Modulator(_Node):

    def prio_all(self) -> _PrioAll:
        return _PrioAll(self._parent_call)

    def prio_p1(self) -> _PrioP1:
        return _PrioP1(self._parent_call)

    def prio_p4(self) -> _PrioP4:
        return _PrioP4(self._parent_call)

    def prio_p7(self) -> _PrioP7:
        return _PrioP7(self._parent_call)

    def prio_ctrl(self) -> _PrioCtrl:
        return _PrioCtrl(self._parent_call)

    def level(self) -> _Level:
        return _Level(self._parent_call)

    def prio_p2(self) -> _PrioP2:
        return _PrioP2(self._parent_call)

    def prio_p3(self) -> _PrioP3:
        return _PrioP3(self._parent_call)

    def prio_p5(self) -> _PrioP5:
        return _PrioP5(self._parent_call)

    def prio_p6(self) -> _PrioP6:
        return _PrioP6(self._parent_call)


class _Tts(_Node):

    def tdelta(self, item_number=0) -> _ReadLeaf:
        """HUB/Outroute - TTS value
Inroute/remote - Timers delta between local station and hub
In 10MHz ticks.
	Developers only"""
        self._oid = '1.3.6.1.4.1.8000.22.5.1.1' + '.' + str(item_number)
        return _ReadLeaf(self._get)

    def tdt_confidence(self, item_number=0) -> _ReadLeaf:
        """HUB/Outroute - TTS confidence value 0-64
Inroute/remote - Tdelta confidence 0-64"""
        self._oid = '1.3.6.1.4.1.8000.22.5.1.2' + '.' + str(item_number)
        return _ReadLeaf(self._get)

    def soft_errors(self, item_number=0) -> _ReadLeaf:
        """Number of soft errors of TTS/Tdelta measurement algorithm.
Soft errors mean current value is outside averaged window."""
        self._oid = '1.3.6.1.4.1.8000.22.5.1.3' + '.' + str(item_number)
        return _ReadLeaf(self._get)

    def hard_errors(self, item_number=0) -> _ReadLeaf:
        """Number of hard errors of TTS/Tdelta measurement algorithm."""
        self._oid = '1.3.6.1.4.1.8000.22.5.1.4' + '.' + str(item_number)
        return _ReadLeaf(self._get)

    def hub_t_t_s(self, item_number=0) -> _ReadLeaf:
        """HUB TTS value in 10MHz ticks"""
        self._oid = '1.3.6.1.4.1.8000.22.5.1.5' + '.' + str(item_number)
        return _ReadLeaf(self._get)

    def hub_t_t_sconfidence(self, item_number=0) -> _ReadLeaf:
        """HUB TTS confidence value 0-64. It is requested from remotes or inroutes"""
        self._oid = '1.3.6.1.4.1.8000.22.5.1.6' + '.' + str(item_number)
        return _ReadLeaf(self._get)

    def remote_t_t_s(self, item_number=0) -> _ReadLeaf:
        """Remote TTS value with compensations in 10MHz ticks. Developers only"""
        self._oid = '1.3.6.1.4.1.8000.22.5.1.7' + '.' + str(item_number)
        return _ReadLeaf(self._get)


class _Inroute(_Node):

    def net_state(self, item_number=0) -> _ReadLeaf:
        """Operation sequence level"""
        self._oid = '1.3.6.1.4.1.8000.22.5.2.1' + '.' + str(item_number)
        return _ReadLeaf(self._get)

    def frame_delay(self, item_number=0) -> _ReadLeaf:
        """Delay in frames between TX and RX processing. Developers only"""
        self._oid = '1.3.6.1.4.1.8000.22.5.2.2' + '.' + str(item_number)
        return _ReadLeaf(self._get)

    def section_b_w(self, item_number=0) -> _ReadLeaf:
        """Bandwidth in Bits/second of single slot in frame"""
        self._oid = '1.3.6.1.4.1.8000.22.5.2.3' + '.' + str(item_number)
        return _ReadLeaf(self._get)

    def net_request(self, item_number=0) -> _ReadLeaf:
        """Sum of all requests of all stations (slots)"""
        self._oid = '1.3.6.1.4.1.8000.22.5.2.4' + '.' + str(item_number)
        return _ReadLeaf(self._get)

    def free_slots(self, item_number=0) -> _ReadLeaf:
        """Number of free-allocated slots in current frame"""
        self._oid = '1.3.6.1.4.1.8000.22.5.2.5' + '.' + str(item_number)
        return _ReadLeaf(self._get)

    def net_load(self, item_number=0) -> _ReadLeaf:
        """Network load in % (values, greater than 100% mean overload)"""
        self._oid = '1.3.6.1.4.1.8000.22.5.2.6' + '.' + str(item_number)
        return _ReadLeaf(self._get)


class _Server(_Node):

    def server_status(self, item_number=0) -> _ReadLeaf:
        """Server reply status"""
        self._oid = '1.3.6.1.4.1.8000.22.5.3.1' + '.' + str(item_number)
        return _ReadLeaf(self._get)

    def frame_duration(self, item_number=0) -> _ReadLeaf:
        """Frame duration in 10M ticks"""
        self._oid = '1.3.6.1.4.1.8000.22.5.3.2' + '.' + str(item_number)
        return _ReadLeaf(self._get)

    def server_faults(self, item_number=0) -> _ReadLeaf:
        """Server faults bitmap: 
0x001   service monitoring local warning (LWRN);
0x002   service monitoring local alarm (LFLT);
0x004   service monitoring network warning (NWRN);
0x008   service monitoring network alarm (NFLT);
0x010   system fault (SYST);
0x020   reboot fault (REBT);
0x040   LAN down (LAN);
0x080   RX1 offset fault (OFFS);
0x100   CRC RX1 errors (CRC);
0x200   TLC fault (TLC);
0x400   RX2 offset fault (OFFS);
0x800   CRC RX2 errors (CRC);
0x1000  CRC BD errors(CRC);"""
        self._oid = '1.3.6.1.4.1.8000.22.5.3.3' + '.' + str(item_number)
        return _ReadLeaf(self._get)


class _RemTable(_Node):

    def rx_bytes(self, item_number=0) -> _ReadLeaf:
        """Summary number of bytes, received from this remote"""
        self._oid = '1.3.6.1.4.1.8000.22.5.4.1' + '.' + str(item_number)
        return _ReadLeaf(self._get)

    def p1_bytes(self, item_number=0) -> _ReadLeaf:
        """Number of P1(Low) priority bytes, received from this remote"""
        self._oid = '1.3.6.1.4.1.8000.22.5.4.2' + '.' + str(item_number)
        return _ReadLeaf(self._get)

    def p4_bytes(self, item_number=0) -> _ReadLeaf:
        """Number of P4(Med) priority bytes, received from this remote"""
        self._oid = '1.3.6.1.4.1.8000.22.5.4.3' + '.' + str(item_number)
        return _ReadLeaf(self._get)

    def p7_bytes(self, item_number=0) -> _ReadLeaf:
        """Number of P7(High) priority bytes, received from this remote"""
        self._oid = '1.3.6.1.4.1.8000.22.5.4.4' + '.' + str(item_number)
        return _ReadLeaf(self._get)

    def crc_errors(self, item_number=0) -> _ReadLeaf:
        """Number of CRC errors, during reception of this remote"""
        self._oid = '1.3.6.1.4.1.8000.22.5.4.5' + '.' + str(item_number)
        return _ReadLeaf(self._get)

    def carrier_to_noise(self, item_number=0) -> _ReadLeaf:
        """Receive carrier-to-noise ratio of this remote in 0.1 dB steps"""
        self._oid = '1.3.6.1.4.1.8000.22.5.4.6' + '.' + str(item_number)
        return _ReadLeaf(self._get)

    def freq_offset(self, item_number=0) -> _ReadLeaf:
        """Receive Frequency offset of this remote in Hz"""
        self._oid = '1.3.6.1.4.1.8000.22.5.4.7' + '.' + str(item_number)
        return _ReadLeaf(self._get)

    def rem_recv_hub(self, item_number=0) -> _ReadLeaf:
        """How this remote receives the hub in 0.1 dB steps"""
        self._oid = '1.3.6.1.4.1.8000.22.5.4.8' + '.' + str(item_number)
        return _ReadLeaf(self._get)

    def link_state(self, item_number=0) -> _ReadLeaf:
        """Link state of this remote"""
        self._oid = '1.3.6.1.4.1.8000.22.5.4.9' + '.' + str(item_number)
        return _ReadLeaf(self._get)

    def last_heard(self, item_number=0) -> _ReadLeaf:
        """Time in seconds since last burst was received from remote. Developers only"""
        self._oid = '1.3.6.1.4.1.8000.22.5.4.10' + '.' + str(item_number)
        return _ReadLeaf(self._get)

    def down_times(self, item_number=0) -> _ReadLeaf:
        """How many times remote changed state to DOWN"""
        self._oid = '1.3.6.1.4.1.8000.22.5.4.11' + '.' + str(item_number)
        return _ReadLeaf(self._get)

    def total_request(self, item_number=0) -> _ReadLeaf:
        """Current non-real-time + real-time request from remote"""
        self._oid = '1.3.6.1.4.1.8000.22.5.4.12' + '.' + str(item_number)
        return _ReadLeaf(self._get)

    def nrt_request(self, item_number=0) -> _ReadLeaf:
        """Current non-real-time request from remote"""
        self._oid = '1.3.6.1.4.1.8000.22.5.4.13' + '.' + str(item_number)
        return _ReadLeaf(self._get)

    def rtm_request(self, item_number=0) -> _ReadLeaf:
        """Current real-time request from remote"""
        self._oid = '1.3.6.1.4.1.8000.22.5.4.14' + '.' + str(item_number)
        return _ReadLeaf(self._get)

    def current_f_p(self, item_number=0) -> _ReadLeaf:
        """Number of sections, allocated in current frame plan for remote"""
        self._oid = '1.3.6.1.4.1.8000.22.5.4.15' + '.' + str(item_number)
        return _ReadLeaf(self._get)

    def tx_lvl(self, item_number=0) -> _ReadLeaf:
        """Current transmit level x -0.1 dBm (1:360 -> -0.1:-36 dBm)"""
        self._oid = '1.3.6.1.4.1.8000.22.5.4.16' + '.' + str(item_number)
        return _ReadLeaf(self._get)

    def faults(self, item_number=0) -> _ReadLeaf:
        """Station faults bitmap: 
0x001   service monitoring local warning (LWRN);
0x002   service monitoring local alarm (LFLT);
0x004   service monitoring network warning (NWRN);
0x008   service monitoring network alarm (NFLT);
0x010   system fault (SYST);
0x020   reboot fault (REBT);
0x040   LAN down (LAN);
0x080   RX1 offset fault (OFFS);
0x100   CRC RX1 errors (CRC);
0x200   TLC fault (TLC);
0x400   RX2 offset fault (OFFS);
0x800   CRC RX2 errors (CRC);
0x1000  CRC BD errors(CRC);"""
        self._oid = '1.3.6.1.4.1.8000.22.5.4.17' + '.' + str(item_number)
        return _ReadLeaf(self._get)

    def p2_bytes(self, item_number=0) -> _ReadLeaf:
        """Number of P2 priority bytes, received from this remote"""
        self._oid = '1.3.6.1.4.1.8000.22.5.4.18' + '.' + str(item_number)
        return _ReadLeaf(self._get)

    def p3_bytes(self, item_number=0) -> _ReadLeaf:
        """Number of P3 priority bytes, received from this remote"""
        self._oid = '1.3.6.1.4.1.8000.22.5.4.19' + '.' + str(item_number)
        return _ReadLeaf(self._get)

    def p5_bytes(self, item_number=0) -> _ReadLeaf:
        """Number of P5 priority bytes, received from this remote"""
        self._oid = '1.3.6.1.4.1.8000.22.5.4.20' + '.' + str(item_number)
        return _ReadLeaf(self._get)

    def p6_bytes(self, item_number=0) -> _ReadLeaf:
        """Number of P6 priority bytes, received from this remote"""
        self._oid = '1.3.6.1.4.1.8000.22.5.4.21' + '.' + str(item_number)
        return _ReadLeaf(self._get)

    def tdma_a_c_m_ch(self, item_number=0) -> _ReadLeaf:
        """TDMA ACM channel station currently in"""
        self._oid = '1.3.6.1.4.1.8000.22.5.4.22' + '.' + str(item_number)
        return _ReadLeaf(self._get)

    def tdm_a_c_m_ch(self, item_number=0) -> _ReadLeaf:
        """TDM ACM channel station currently in"""
        self._oid = '1.3.6.1.4.1.8000.22.5.4.23' + '.' + str(item_number)
        return _ReadLeaf(self._get)


class _Station(_Node):

    def station_state(self, item_number=0) -> _ReadLeaf:
        """Remote initialization sequence level"""
        self._oid = '1.3.6.1.4.1.8000.22.5.5.1' + '.' + str(item_number)
        return _ReadLeaf(self._get)

    def remnrt_request(self, item_number=0) -> _ReadLeaf:
        """Request for non-real-time bandwidth in sections"""
        self._oid = '1.3.6.1.4.1.8000.22.5.5.2' + '.' + str(item_number)
        return _ReadLeaf(self._get)

    def remrt_request(self, item_number=0) -> _ReadLeaf:
        """Request for real-time bandwidth in sections"""
        self._oid = '1.3.6.1.4.1.8000.22.5.5.3' + '.' + str(item_number)
        return _ReadLeaf(self._get)

    def fp_lost(self, item_number=0) -> _ReadLeaf:
        """Lost frame plans number"""
        self._oid = '1.3.6.1.4.1.8000.22.5.5.4' + '.' + str(item_number)
        return _ReadLeaf(self._get)

    def lvl_offset(self, item_number=0) -> _ReadLeaf:
        """Offset between reference level and C/N level on hub. Developers only"""
        self._oid = '1.3.6.1.4.1.8000.22.5.5.5' + '.' + str(item_number)
        return _ReadLeaf(self._get)

    def lvl_adjust(self, item_number=0) -> _ReadLeaf:
        """TX power level adjustment value in 0.1 dB steps"""
        self._oid = '1.3.6.1.4.1.8000.22.5.5.6' + '.' + str(item_number)
        return _ReadLeaf(self._get)

    def frq_offset(self, item_number=0) -> _ReadLeaf:
        """Frequency offset on hub. Developers only"""
        self._oid = '1.3.6.1.4.1.8000.22.5.5.7' + '.' + str(item_number)
        return _ReadLeaf(self._get)

    def frq_adjust(self, item_number=0) -> _ReadLeaf:
        """TX frequency adjustment value in Hz. Developers only"""
        self._oid = '1.3.6.1.4.1.8000.22.5.5.8' + '.' + str(item_number)
        return _ReadLeaf(self._get)

    def time_offset(self, item_number=0) -> _ReadLeaf:
        """Timing offset on hub in symbols"""
        self._oid = '1.3.6.1.4.1.8000.22.5.5.9' + '.' + str(item_number)
        return _ReadLeaf(self._get)

    def time_adjust(self, item_number=0) -> _ReadLeaf:
        """TX timing adjustment value in 10M ticks"""
        self._oid = '1.3.6.1.4.1.8000.22.5.5.10' + '.' + str(item_number)
        return _ReadLeaf(self._get)


class _Tdma(_Node):

    def tts(self) -> _Tts:
        return _Tts(self._parent_call)

    def inroute(self) -> _Inroute:
        return _Inroute(self._parent_call)

    def server(self) -> _Server:
        return _Server(self._parent_call)

    def rem_table(self) -> _RemTable:
        return _RemTable(self._parent_call)

    def station(self) -> _Station:
        return _Station(self._parent_call)


class _Router(_Node):

    def unrouted_pkts(self, item_number=0) -> _ReadLeaf:
        """Number of packets, router couldn't route anywhere
(though they could have been tunneled)."""
        self._oid = '1.3.6.1.4.1.8000.22.6.1' + '.' + str(item_number)
        return _ReadLeaf(self._get)

    def unrouted_source(self, item_number=0) -> _ReadLeaf:
        """Last source IP address of unrouted packet."""
        self._oid = '1.3.6.1.4.1.8000.22.6.2' + '.' + str(item_number)
        return _ReadLeaf(self._get)

    def unrouted_dest(self, item_number=0) -> _ReadLeaf:
        """Last destination IP address of unrouted packet."""
        self._oid = '1.3.6.1.4.1.8000.22.6.3' + '.' + str(item_number)
        return _ReadLeaf(self._get)

    def out_vlan_bytes(self, item_number=0) -> _ReadLeaf:
        """Number of bytes, transmitted via VLAN.
Requires index, which is VLAN number."""
        self._oid = '1.3.6.1.4.1.8000.22.6.4' + '.' + str(item_number)
        return _ReadLeaf(self._get)

    def in_vlan_bytes(self, item_number=0) -> _ReadLeaf:
        """Number of bytes, received via VLAN.
Requires index, which is VLAN number."""
        self._oid = '1.3.6.1.4.1.8000.22.6.5' + '.' + str(item_number)
        return _ReadLeaf(self._get)

    def out_svlan_bytes(self, item_number=0) -> _ReadLeaf:
        """Number of bytes, transmitted via SVLAN.
Requires index, which is SVLAN number."""
        self._oid = '1.3.6.1.4.1.8000.22.6.6' + '.' + str(item_number)
        return _ReadLeaf(self._get)

    def in_svlan_bytes(self, item_number=0) -> _ReadLeaf:
        """Number of bytes, received via SVLAN.
Requires index, which is SVLAN number."""
        self._oid = '1.3.6.1.4.1.8000.22.6.7' + '.' + str(item_number)
        return _ReadLeaf(self._get)

    def in_svlan_packets(self, item_number=0) -> _ReadLeaf:
        """Number of packets, received via SVLAN.
Requires index, which is SVLAN number."""
        self._oid = '1.3.6.1.4.1.8000.22.6.8' + '.' + str(item_number)
        return _ReadLeaf(self._get)


class _Shaper(_Node):

    def stream_speed(self, item_number=0) -> _ReadLeaf:
        """Current speed in Kbits per second of current stream"""
        self._oid = '1.3.6.1.4.1.8000.22.7.1' + '.' + str(item_number)
        return _ReadLeaf(self._get)

    def stream_p1_speed(self, item_number=0) -> _ReadLeaf:
        """Current speed in Kbits per second of P1(Low) priority sub-stream"""
        self._oid = '1.3.6.1.4.1.8000.22.7.2' + '.' + str(item_number)
        return _ReadLeaf(self._get)

    def stream_p4_speed(self, item_number=0) -> _ReadLeaf:
        """Current speed in Kbits per second of P4(Med) priority sub-stream"""
        self._oid = '1.3.6.1.4.1.8000.22.7.3' + '.' + str(item_number)
        return _ReadLeaf(self._get)

    def stream_p7_speed(self, item_number=0) -> _ReadLeaf:
        """Current speed in Kbits per second of P7(High) priority sub-stream"""
        self._oid = '1.3.6.1.4.1.8000.22.7.4' + '.' + str(item_number)
        return _ReadLeaf(self._get)

    def stream_delay(self, item_number=0) -> _ReadLeaf:
        """Current packets delay in stream x 0.1s"""
        self._oid = '1.3.6.1.4.1.8000.22.7.5' + '.' + str(item_number)
        return _ReadLeaf(self._get)

    def stream_p2_speed(self, item_number=0) -> _ReadLeaf:
        """Current speed in Kbits per second of P2 priority sub-stream"""
        self._oid = '1.3.6.1.4.1.8000.22.7.7' + '.' + str(item_number)
        return _ReadLeaf(self._get)

    def stream_p3_speed(self, item_number=0) -> _ReadLeaf:
        """Current speed in Kbits per second of P3 priority sub-stream"""
        self._oid = '1.3.6.1.4.1.8000.22.7.8' + '.' + str(item_number)
        return _ReadLeaf(self._get)

    def stream_p5_speed(self, item_number=0) -> _ReadLeaf:
        """Current speed in Kbits per second of P5 priority sub-stream"""
        self._oid = '1.3.6.1.4.1.8000.22.7.9' + '.' + str(item_number)
        return _ReadLeaf(self._get)

    def stream_p6_speed(self, item_number=0) -> _ReadLeaf:
        """Current speed in Kbits per second of P6 priority sub-stream"""
        self._oid = '1.3.6.1.4.1.8000.22.7.10' + '.' + str(item_number)
        return _ReadLeaf(self._get)


class _System1(_Node):

    def temperature(self, item_number=0) -> _ReadLeaf:
        """Current temperature"""
        self._oid = '1.3.6.1.4.1.8000.22.8.1' + '.' + str(item_number)
        return _ReadLeaf(self._get)

    def cpu_load(self, item_number=0) -> _ReadLeaf:
        """Current CPU load in percent"""
        self._oid = '1.3.6.1.4.1.8000.22.8.2' + '.' + str(item_number)
        return _ReadLeaf(self._get)

    def buffers(self, item_number=0) -> _ReadLeaf:
        """Current buffers usage in percent"""
        self._oid = '1.3.6.1.4.1.8000.22.8.3' + '.' + str(item_number)
        return _ReadLeaf(self._get)

    def redundancy(self, item_number=0) -> _ReadLeaf:
        """Current redundancy state"""
        self._oid = '1.3.6.1.4.1.8000.22.8.4' + '.' + str(item_number)
        return _ReadLeaf(self._get)

    def sw_version(self, item_number=0) -> _ReadLeaf:
        """Software version. Four numbers of version contained in four bytes
in order of precedence (see as hexadecimal)."""
        self._oid = '1.3.6.1.4.1.8000.22.8.5' + '.' + str(item_number)
        return _ReadLeaf(self._get)

    def release_date(self, item_number=0) -> _ReadLeaf:
        """Release date. Two low bytes of number contain year,
then month and day (see as hexadecimal)."""
        self._oid = '1.3.6.1.4.1.8000.22.8.6' + '.' + str(item_number)
        return _ReadLeaf(self._get)


class _Mobile(_Node):

    def version(self, item_number=0) -> _ReadLeaf:
        """Software (protocol) version. Number 10 means V1.0"""
        self._oid = '1.3.6.1.4.1.8000.22.9.1' + '.' + str(item_number)
        return _ReadLeaf(self._get)

    def serial_number(self, item_number=0) -> _ReadLeaf:
        """Serial number of this unit. If printed on the screen should be 
printed as hexadecimal! Example - 4660 returned should be printed 
as 1234 in hex."""
        self._oid = '1.3.6.1.4.1.8000.22.9.2' + '.' + str(item_number)
        return _ReadLeaf(self._get)

    def input_level(self, item_number=0) -> _ReadLeaf:
        """Input baseband RF level in -0.1dBm steps. 500 means -50 dBm.
Higher value means lower level. 800 (-80dBm) means no signal."""
        self._oid = '1.3.6.1.4.1.8000.22.9.3' + '.' + str(item_number)
        return _ReadLeaf(self._get)

    def rx_state(self, item_number=0) -> _ReadLeaf:
        """Composite value to provide controller with receive and overall state.
0 means no RX lock.
1 means absence of coordinates (send location data).
2 means absence of TX status (send TX control command).
3-250 means RX lock and shows demodulator C/N level in 0.1dBm 
	steps (e.g. 100 means C/N=10 dB).
Actual in all modes of operation. In SCPC/Star modes shows
SCPC demodulator level, in FullMesh mode burst demodulator level."""
        self._oid = '1.3.6.1.4.1.8000.22.9.4' + '.' + str(item_number)
        return _ReadLeaf(self._get)

    def search_state(self, item_number=0) -> _ReadWriteLeaf:
        """GET
Value in percent (0-100) of current carrier search sequence.
As search for narrow (<1Msps) carrier with high offset (DRO
LNB) can last up-to 30 seconds, controller can wait until
the whole acquisition bandwidth is scanned at least once.
SET
Writing any value restarts search cycle."""
        self._oid = '1.3.6.1.4.1.8000.22.9.5' + '.' + str(item_number)
        return _ReadWriteLeaf(self._get, self._set)

    def tx_control(self, item_number=0) -> _ReadWriteLeaf:
        """GET
Current TX status (0-off, 1-on).
SET
Writing 0 turns TX off, 1 - turns on."""
        self._oid = '1.3.6.1.4.1.8000.22.9.6' + '.' + str(item_number)
        return _ReadWriteLeaf(self._get, self._set)

    def location(self, item_number=0) -> _ReadWriteLeaf:
        """GET
Not applicable.
SET
NMEA RMC string
$GPRMC,hhmmss.ss,A,GGMM.MM,P,gggmm.mm,J,v.v,b.b,ddmmyy,x.x,n,m*hh<CR><LF>
Location should be re-supplied if changed more than 1 minute by any 	     coordinate."""
        self._oid = '1.3.6.1.4.1.8000.22.9.7' + '.' + str(item_number)
        return _ReadWriteLeaf(self._get, self._set)


class UhpSnmpDriver(AbstractUhpSnmp):

    def mib2(self) -> _Mib2:
        return _Mib2(self._call)

    def control(self) -> _Control:
        return _Control(self._call)

    def demod1(self) -> _Demod1:
        return _Demod1(self._call)

    def demod2(self) -> _Demod2:
        return _Demod2(self._call)

    def modulator(self) -> _Modulator:
        return _Modulator(self._call)

    def tdma(self) -> _Tdma:
        return _Tdma(self._call)

    def router(self) -> _Router:
        return _Router(self._call)

    def shaper(self) -> _Shaper:
        return _Shaper(self._call)

    def system(self) -> _System1:
        return _System1(self._call)

    def mobile(self) -> _Mobile:
        return _Mobile(self._call)
