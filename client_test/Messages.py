dhcp_discover = {
    'op': b'01',
    'htype': b'01',
    'hlen': b'06',
    'hops': b'00',
    'xid': b'28a248a3',
    'secs': b'0000',
    'flags': b'8000',
    'ciaddr': b'00000000',
    'yiaddr': b'00000000',
    'siaddr': b'00000000',
    'giaddr': b'00000000',
    'chaddr': b'9439e59fecaf00000000000000000000',
    'sname': b'00' * 64,
    'file': b'00' * 128,
    'magic cookie': b'63825363',
    'options': b'350101' +
               b'3d079439e59fecaf54' +
               b'3204c0a80075' +
               b'0c09466c6f72696e2d5043' +
               b'3c084d53465420352e30' +
               b'370c010f03062c2e2f1f2179f92b' +
               b'ff'
}

dhcp_discover2 = {
    'op': b'01',
    'htype': b'01',
    'hlen': b'06',
    'hops': b'00',
    'xid': b'28a248a3',
    'secs': b'0000',
    'flags': b'8000',
    'ciaddr': b'00000000',
    'yiaddr': b'00000000',
    'siaddr': b'00000000',
    'giaddr': b'00000000',
    'chaddr': b'9239e59fecaf00000000000000000000',
    'sname': b'00' * 64,
    'file': b'00' * 128,
    'magic cookie': b'63825363',
    'options': b'350101' +
               b'3d079439e59fecaf54' +
               b'3204c0a80015' +
               b'0c09466c6f72696e2d5043' +
               b'3c084d53465420352e30' +
               b'370c0103062c2e2f1f21f92b' +
               b'ff'
}

dhcp_requestsel = {
    'op': b'01',
    'htype': b'01',
    'hlen': b'06',
    'hops': b'00',
    'xid': b'28a248a3',
    'secs': b'0000',
    'flags': b'8000',
    'ciaddr': b'00000000',
    'yiaddr': b'00000000',
    'siaddr': b'00000000',
    'giaddr': b'00000000',
    'chaddr': b'9439e59fecaf00000000000000000000',
    'sname': b'00' * 64,
    'file': b'00' * 128,
    'magic cookie': b'63825363',
    'options': b'350103' +
               b'3204c0a80075' +
               b'3d079439e59fecaf54' +
               b'3604c0a800fe' +
               b'0c09466c6f72696e2d5043' +
               b'3c084d53465420352e30' +
               b'370c010f03062c2e2f1f2179f92b' +
               b'ff'
}

dhcp_requestinit = {
    'op': b'01',
    'htype': b'01',
    'hlen': b'06',
    'hops': b'00',
    'xid': b'28a248a3',
    'secs': b'0000',
    'flags': b'8000',
    'ciaddr': b'00000000',
    'yiaddr': b'00000000',
    'siaddr': b'00000000',
    'giaddr': b'00000000',
    'chaddr': b'9439e59fecaf00000000000000000000',
    'sname': b'00' * 64,
    'file': b'00' * 128,
    'magic cookie': b'63825363',
    'options': b'350103' +
               b'3204c0a80075' +
               b'3d079439e59fecaf54' +
               b'0c09466c6f72696e2d5043' +
               b'3c084d53465420352e30' +
               b'370c010f03062c2e2f1f2179f92b' +
               b'ff'
}

dhcp_decline = {
    'op': b'01',
    'htype': b'01',
    'hlen': b'06',
    'hops': b'00',
    'xid': b'28a248a3',
    'secs': b'0000',
    'flags': b'0000',
    'ciaddr': b'00000000',
    'yiaddr': b'00000000',
    'siaddr': b'00000000',
    'giaddr': b'00000000',
    'chaddr': b'9439e59fecaf00000000000000000000',
    'sname': b'00' * 64,
    'file': b'00' * 128,
    'magic cookie': b'63825363',
    'options': b'350104' +
               b'3204c0a80075' +
               b'3604c0a800fe' +
               b'ff'
}

dhcp_release = {
    'op': b'01',
    'htype': b'01',
    'hlen': b'06',
    'hops': b'00',
    'xid': b'28a248a3',
    'secs': b'0000',
    'flags': b'0000',
    'ciaddr': b'00000000',
    'yiaddr': b'00000000',
    'siaddr': b'00000000',
    'giaddr': b'00000000',
    'chaddr': b'9439e59fecaf00000000000000000000',
    'sname': b'00' * 64,
    'file': b'00' * 128,
    'magic cookie': b'63825363',
    'options': b'350107' +
               b'3604c0a800fe' +
               b'ff'
}

dhcp_inform = {
    'op': b'01',
    'htype': b'01',
    'hlen': b'06',
    'hops': b'00',
    'xid': b'28a248a3',
    'secs': b'0000',
    'flags': b'8000',
    'ciaddr': b'00000000',
    'yiaddr': b'00000000',
    'siaddr': b'00000000',
    'giaddr': b'00000000',
    'chaddr': b'9439e59fecaf00000000000000000000',
    'sname': b'00' * 64,
    'file': b'00' * 128,
    'magic cookie': b'63825363',
    'options': b'350108' +
               b'3d079439e59fecaf54' +
               b'370c010f03062c2e2f1f2179f92b' +
               b'ff'
}
