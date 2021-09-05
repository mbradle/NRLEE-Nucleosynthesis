import sys
import numpy as np
import wnutils.xml as wx

def write_zone_xml(zone, dir):

    f = open(dir + "/" + zone + ".xml", 'w')
    f.write(
        "<?xml version=\"1.0\" encoding=\"ISO-8859-1\"?>\n\
         <libnucnet_input\n\
            xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\"\n\
            xmlns:xi=\"http://www.w3.org/2001/XInclude\"\n\
         >\n\
           <nuclear_network>\n\
             <xi:include href=\"../full.xml\"\n\
             xpointer=\"xpointer(//nuclear_network)\" />\n\
           </nuclear_network>\n\
           <zone_data>\n\
             <xi:include href=\"../" + sys.argv[3] + "/" + zone + ".xml\"\n\
             xpointer=\"xpointer(//zone)\" />\n\
           </zone_data>\n\
         </libnucnet_input>")
    f.close()

rhos = np.genfromtxt(sys.argv[1], dtype='str')

for rho in rhos:
    xmlz = wx.Xml(sys.argv[2] + '/' + rho + '.xml')
    new_zones = xmlz.get_zone_data()
    new_xml = wx.New_Xml(xml_type='zone_data')
    new_xml.set_zone_data(new_zones)
    new_xml.write(sys.argv[2] + '/' + sys.argv[3] + '/' + rho + '.xml')
    write_zone_xml(rho, sys.argv[2] + '/' + sys.argv[4])

xml = wx.Xml(sys.argv[2] + '/' + rhos[0] + '.xml')
new_full_xml = wx.New_Xml(xml_type='libnucnet_input')
new_full_xml.set_nuclide_data(xml.get_nuclide_data())
new_full_xml.set_reaction_data(xml.get_reaction_data())

zones = {}
for rho in rhos:
    xmlz = wx.Xml(sys.argv[2] + '/' + sys.argv[3] + '/' + rho + '.xml')
    old_zone = xmlz.get_zone_data("[last()]")
    zones[rho] = old_zone.pop(list(old_zone.keys())[0])

new_full_xml.set_zone_data(zones)
new_full_xml.write(sys.argv[2] + '/' + sys.argv[5])
