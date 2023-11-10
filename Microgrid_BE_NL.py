#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 18 11:05:18 2023

@author: juliangiraldo
"""

# %%
import pandapower as pp
import xml.etree.ElementTree as ET
# import os
# import pandapower.plotting as pp_plot
# os.environ["MAPBOX_ACCESS_TOKEN"]= "pk.eyJ1IjoiamdpcmFsZG9ybTciLCJhIjoiY2xvc3hjbjQ3MDV3cDJtcTBqdjJydWwxOCJ9.HPndplEdl0aUdHKTRGcRAQ"

#%%
# Creation of all the classes considered as essential elements to later build the representation of the power system
class ACLineSegment:
    def __init__(self, ID, name, equipment_container, r,
                 x, bch, length, gch, base_voltage, r0, x0, b0ch, 
                 g0ch):
        self.ID = ID
        self.name = name
        self.equipment_container = equipment_container
        self.r = r
        self.x = x
        self.bch = bch
        self.length = length
        self.gch = gch
        self.base_voltage = base_voltage
        self.r0 = r0
        self.x0 = x0
        self.b0ch = b0ch
        self.g0ch = g0ch

class BaseVoltage:
    def __init__(self, name,  ID, nominalVoltage):
        self.name = name
        self.ID = ID
        self.nominalVoltage = nominalVoltage

class Breaker:
    def __init__(self, ID, name, equipment_container, status):
        self.ID = ID
        self.name = name
        self.equipment_container = equipment_container
        self.status = status

class BusbarSection:
    def __init__(self, ID, name, equipment_container):
        self.ID = ID
        self.name = name
        self.equipment_container = equipment_container

class ConnectivityNode:
    def __init__(self, ID, name, connectivity_node_container):
        self.ID = ID
        self.name = name
        self.connectivity_node_container = connectivity_node_container
        
class EnergyConsumer:
    def __init__(self, ID, name, equipment_container, active_power, 
                 reactive_power):
        self.ID = ID
        self.name = name
        self.equipment_container = equipment_container
        self.active_power = active_power
        self.reactive_power = reactive_power
        
class GeneratingUnit:
    def __init__(self, ID, name, initialP, nominalP, 
                 maxOperatingP, minOperatingP, genControlSource, 
                 equipment_container):
        self.ID = ID
        self.name = name
        self.initialP = initialP
        self.nominalP = nominalP
        self.maxOperatingP = maxOperatingP
        self.minOperatingP = minOperatingP
        self.genControlSource = genControlSource
        self.equipment_container = equipment_container

class GeographicalRegion:
    def __init__(self, ID, name):
        self.ID = ID
        self.name = name

class Line:
    def __init__(self, ID, name, region):
        self.ID = ID
        self.name = name
        self.region = region

class LinearShuntCompensator:
    def __init__(self, ID, name, b_per_section, g_per_section, b0_per_section, 
                 g0_per_section, nom_u, regulating_control, equipment_container):
        self.ID = ID
        self.name = name
        self.b_per_section = b_per_section
        self.g_per_section = g_per_section 
        self.b0_per_section = b0_per_section
        self.g0_per_section = g0_per_section
        self.nom_u = nom_u
        self.regulating_control = regulating_control
        self.equipment_container = equipment_container
        self.q_mvar_sh= ''
        
class PowerTransformer:
    def __init__(self, ID, name, equipment_container):
        self.ID = ID
        self.name = name
        self.equipment_container = equipment_container
        

class PowerTransformerEnd:
    def __init__(self, ID, name, short_name, r, x, b, g, r0, x0, b0, g0, 
                 rground, xground, rated_s, rated_u, phase_angle_clock, 
                 connection_kind, base_voltage, power_transformer, terminal):
        self.ID = ID
        self.name = name
        self.short_name = short_name
        self.r = r
        self.x = x
        self.b = b
        self.g = g
        self.r0 = r0 
        self.x0 = x0
        self.b0 = b0
        self.g0 = g0
        self.rground = rground
        self.xground = xground
        self.rated_s = rated_s
        self.rated_u = rated_u 
        self.phase_angle_clock = phase_angle_clock
        self.connection_kind = connection_kind
        self.base_voltage = base_voltage
        self.power_transformer = power_transformer
        self.terminal = terminal

class RatioTapChanger:
    def __init__(self, ID, name, transformer_end, step):
        self.ID = ID
        self.name = name
        self.transformer_end = transformer_end
        self.step = step
       
        
class RegulatingControl:
    def __init__(self, ID, name, mode, terminal, target_value):
        self.ID = ID
        self.name = name
        self.mode = mode
        self.terminal = terminal
        self.target_value = target_value

class Substation:
    def __init__(self, ID, name, region):
        self.ID = ID
        self.name = name
        self.region = region     

class SynchronousMachine: 
    def __init__(self, ID, name, equipment_container, regulating_control, 
                 generating_unit, active_power, reactive_power):
        self.ID = ID
        self.name = name
        self.equipment_container = equipment_container
        self.regulating_control = regulating_control
        self.generating_unit = generating_unit
        self.active_power = active_power
        self.reactive_power = reactive_power
        
class Terminal:
    def __init__(self, ID, name, conducting_equipment, connectivity_node):
        self.ID = ID
        self.name = name
        self.conducting_equipment = conducting_equipment
        self.connectivity_node = connectivity_node

class VoltageLevel:
    def __init__(self, ID, name, substation, base_voltage):
        self.ID = ID
        self.name = name
        self.substation = substation
        self.base_voltage = base_voltage
        
    def __print__(self):
        print(self.ID + " " + self.name)


# %%
#Creation of a class called "maestro" which contains three different functions which are mainly the parsing of the xml files
#Construction of the powwer system representation for each country and finally the one which allows to print the created topology for each country
#By having this class, the parsing, extraction of information, plottin gof the network and weverything can be done for each country (BE and NL)
#without the need of rewrite the program twice , once for each country.
class maestro:
    def __init__(self, country_EQ_tree, country_SSH_tree, cim, rdf, md) -> vars:
        
        self.country_EQ_tree = country_EQ_tree
        self.country_SSH_tree = country_SSH_tree
        # Getting the root of the three
        self.country_EQ_root = country_EQ_tree.getroot()
        self.country_SSH_root = country_SSH_tree.getroot()
    
        cim = cim
        rdf = rdf
        md = md

    def xml_extraction(self):
            
        # Create dictionary that will contain all th einformation for the network of the country 
        dic_country = {}
        # Defining the keys' names based on the previous classes created and the information considered as relevant 
        names = ['AC_line_segment_xml','base_voltage_xml', 'breaker_xml', 'busbar_section_xml',
                'connectivity_node_xml', 'energy_consumer_xml','generating_unit_xml',
                'geographical_region_xml', 'line_xml', 'linear_shunt_compensator_xml', 
                'power_transformer_xml', 'power_transformer_end_xml', 'ratio_tap_changer_xml',
                    'regulating_control_xml', 'substation_xml', 'synchronous_machine_xml',
                    'terminal_xml', 'voltage_level_xml']
        
        # Assigning the features to every of the keys
        for _ in names:
            dic_country[_] = []
            if 'AC_line_segment_xml' == _:
                for AC_line_segment_xml in self.country_EQ_root.iter(cim+'ACLineSegment'):
                    # print(AC_line_segment_xml)
                    dic_country[_].append(ACLineSegment(AC_line_segment_xml.get(rdf+'ID'),
                    AC_line_segment_xml.find(cim+'IdentifiedObject.name').text,
                    AC_line_segment_xml.find(cim+'Equipment.EquipmentContainer').get(rdf+'resource'),
                    AC_line_segment_xml.find(cim+'ACLineSegment.r').text, 
                    AC_line_segment_xml.find(cim+'ACLineSegment.x').text, 
                    AC_line_segment_xml.find(cim+'ACLineSegment.bch').text,
                    AC_line_segment_xml.find(cim+'Conductor.length').text,
                    AC_line_segment_xml.find(cim+'ACLineSegment.gch').text,
                    AC_line_segment_xml.find(cim+'ConductingEquipment.BaseVoltage').get(rdf+'resource'),  
                    AC_line_segment_xml.find(cim+"ACLineSegment.r0"), 
                    AC_line_segment_xml.find(cim+"ACLineSegment.x0"), 
                    AC_line_segment_xml.find(cim+"ACLineSegment.b0ch"),
                    AC_line_segment_xml.find(cim+"ACLineSegment.g0ch")))
            if 'base_voltage_xml' == _:       
                for base_voltage_xml in self.country_EQ_root.iter(cim+'BaseVoltage'):
                    dic_country[_].append(BaseVoltage(base_voltage_xml.get(rdf+'ID'),
                    base_voltage_xml.find(cim+'IdentifiedObject.name').text,                              
                    base_voltage_xml.find(cim+'BaseVoltage.nominalVoltage').text))
            if 'breaker_xml' == _:
                for breaker_xml in self.country_EQ_root.iter(cim+'Breaker'):
                    dic_country[_].append(Breaker(breaker_xml.get(rdf+'ID'), 
                    breaker_xml.find(cim+'IdentifiedObject.name').text,
                    breaker_xml.find(cim+'Equipment.EquipmentContainer').get(rdf+'resource'),
                    " "))            
                # Using zip in order to be able to assign the features from the SSH file as well for different equipments as for in this case the breakers
                for i, breaker_xml  in zip(range(len(list(self.country_SSH_root.iter(cim+"Breaker")))), self.country_SSH_root.iter(cim+"Breaker")): 
                    dic_country[_][i].status=breaker_xml.find(cim+"Switch.open").text
            if 'busbar_section_xml' == _:    
                for busbar_section_xml in self.country_EQ_root.iter(cim+'BusbarSection'):
                    dic_country[_].append(BusbarSection(busbar_section_xml.get(rdf+'ID'), 
                    busbar_section_xml.find(cim+'IdentifiedObject.name').text, 
                    busbar_section_xml.find(cim+'Equipment.EquipmentContainer').get(rdf+'resource')))
            if 'connectivity_node_xml' == _: 
                for connectivity_node_xml in self.country_EQ_root.iter(cim+'ConnectivityNode'):
                    dic_country[_].append(ConnectivityNode(connectivity_node_xml.get(rdf+'ID'), 
                    connectivity_node_xml.find(cim+'IdentifiedObject.name').text, 
                    connectivity_node_xml.find(cim+"ConnectivityNode.ConnectivityNodeContainer").get(rdf+"resource")))
            if 'energy_consumer_xml' == _: 
                for energy_consumer_xml in self.country_EQ_root.iter(cim+'EnergyConsumer'):
                    dic_country[_].append(EnergyConsumer(energy_consumer_xml.get(rdf+'ID'), 
                    energy_consumer_xml.find(cim+'IdentifiedObject.name').text,
                    energy_consumer_xml.find(cim+'Equipment.EquipmentContainer').get(rdf+'resource'), 
                    "", ""))   
                # Using zip in order to be able to assign the features from the SSH file as well for different equipments as for in this case the Energy Consumer
                for i, energy_consumer_xml in zip(range(len(list(self.country_SSH_root.iter(cim+'EnergyConsumer')))), self.country_SSH_root.iter(cim+'EnergyConsumer')):
                    dic_country[_][i].active_power=energy_consumer_xml.find(cim+"EnergyConsumer.p").text
                    dic_country[_][i].reactive_power=energy_consumer_xml.find(cim+"EnergyConsumer.q").text

            if 'generating_unit_xml' == _: 
                for generating_unit_xml in self.country_EQ_root.iter(cim+'GeneratingUnit'):
                    dic_country[_].append(GeneratingUnit(generating_unit_xml.get(rdf+'ID'), 
                    generating_unit_xml.find(cim+'IdentifiedObject.name').text, 
                    generating_unit_xml.find(cim+"GeneratingUnit.initialP").text,
                    generating_unit_xml.find(cim+"GeneratingUnit.nominalP").text,
                    generating_unit_xml.find(cim+'GeneratingUnit.maxOperatingP').text, 
                    generating_unit_xml.find(cim+'GeneratingUnit.minOperatingP').text,
                    generating_unit_xml.find(cim+"GeneratingUnit.genControlSource").get(rdf+'resource'),
                    generating_unit_xml.find(cim+'Equipment.EquipmentContainer').get(rdf+'resource'))) 
            
            if 'geographical_region_xml' == _: 
                for geographical_region_xml in self.country_EQ_root.iter(cim+'GeographicalRegion'):
                    dic_country[_].append(GeographicalRegion(geographical_region_xml.get(rdf+'ID'), 
                    geographical_region_xml.find(cim+'IdentifiedObject.name').text))
            
            if 'line_xml' == _: 
                for line_xml in self.country_EQ_root.iter(cim+'Line'):
                    dic_country[_].append(Line(line_xml.get(rdf+'ID'), 
                    line_xml.find(cim+'IdentifiedObject.name').text,
                    line_xml.find(cim+'Line.Region').get(rdf+'resource')))

            if 'linear_shunt_compensator_xml' == _: 
                for linear_shunt_compensator_xml in self.country_EQ_root.iter(cim+'LinearShuntCompensator'):
                    dic_country[_].append(LinearShuntCompensator(linear_shunt_compensator_xml.get(rdf+'ID'), 
                    linear_shunt_compensator_xml.find(cim+'IdentifiedObject.name').text, 
                    linear_shunt_compensator_xml.find(cim+'LinearShuntCompensator.bPerSection').text,
                    linear_shunt_compensator_xml.find(cim+'LinearShuntCompensator.gPerSection').text,
                    linear_shunt_compensator_xml.find(cim+'LinearShuntCompensator.b0PerSection').text,
                    linear_shunt_compensator_xml.find(cim+'LinearShuntCompensator.g0PerSection').text,
                    linear_shunt_compensator_xml.find(cim+'ShuntCompensator.nomU').text,
                    linear_shunt_compensator_xml.find(cim+'RegulatingCondEq.RegulatingControl').get(rdf+'resource'),
                    linear_shunt_compensator_xml.find(cim+'Equipment.EquipmentContainer').get(rdf+'resource')))
            
            if 'power_transformer_xml' == _:
                for power_transformer_xml in self.country_EQ_root.iter(cim+'PowerTransformer'):
                    dic_country[_].append(PowerTransformer(power_transformer_xml.get(rdf+'ID'), 
                    power_transformer_xml.find(cim+'IdentifiedObject.name').text,
                    power_transformer_xml.find(cim+'Equipment.EquipmentContainer').get(rdf+'resource')))

            if 'power_transformer_end_xml' == _:
                for power_transformer_end_xml in self.country_EQ_root.iter(cim+'PowerTransformerEnd'):
                    dic_country[_].append(PowerTransformerEnd(power_transformer_end_xml.get(rdf+'ID'),
                    power_transformer_end_xml.find(cim+'IdentifiedObject.name').text, 
                    power_transformer_end_xml.find(cim+'PowerTransformerEnd.r').text,
                    power_transformer_end_xml.find(cim+'PowerTransformerEnd.x').text,
                    power_transformer_end_xml.find(cim+'PowerTransformerEnd.b').text,
                    power_transformer_end_xml.find(cim+'PowerTransformerEnd.g').text,
                    power_transformer_end_xml.find(cim+'PowerTransformerEnd.r0').text,
                    power_transformer_end_xml.find(cim+'PowerTransformerEnd.x0').text,
                    power_transformer_end_xml.find(cim+'PowerTransformerEnd.b0').text,
                    power_transformer_end_xml.find(cim+'PowerTransformerEnd.g0').text,
                    power_transformer_end_xml.find(cim+'TransformerEnd.rground').text,
                    power_transformer_end_xml.find(cim+'TransformerEnd.xground').text,
                    power_transformer_end_xml.find(cim+'PowerTransformerEnd.ratedS').text,
                    power_transformer_end_xml.find(cim+'PowerTransformerEnd.ratedU').text,
                    power_transformer_end_xml.find(cim+'TransformerEnd.endNumber').text,
                    power_transformer_end_xml.find(cim+'PowerTransformerEnd.phaseAngleClock').text,
                    power_transformer_end_xml.find(cim+'PowerTransformerEnd.connectionKind').get(rdf+'resource'),
                    power_transformer_end_xml.find(cim+'TransformerEnd.BaseVoltage').get(rdf+'resource'),
                    power_transformer_end_xml.find(cim+'PowerTransformerEnd.PowerTransformer').get(rdf+'resource'), 
                    power_transformer_end_xml.find(cim+'TransformerEnd.Terminal').get(rdf+'resource')))

            if 'ratio_tap_changer_xml' == _:
                for ratio_tap_changer_xml in self.country_EQ_root.iter(cim+'RatioTapChanger'):
                    dic_country[_].append(RatioTapChanger(ratio_tap_changer_xml.get(rdf+'ID'), 
                    ratio_tap_changer_xml.find(cim+'IdentifiedObject.name').text, 
                    ratio_tap_changer_xml.find(cim+'RatioTapChanger.TransformerEnd').get(rdf+'resource'),
                    ""))
                for i, ratio_tap_changer_xml in zip(range(len(list(self.country_SSH_root.iter(cim+'RatioTapChanger')))), self.country_SSH_root.iter(cim+'RatioTapChanger')):
                    dic_country[_][i].step = ratio_tap_changer_xml.find(cim+'TapChanger.step').text
        
            if 'regulating_control_xml' == _:
                for regulating_control_xml in self.country_EQ_root.iter(cim+'RegulatingControl'):
                    dic_country[_].append(RegulatingControl(regulating_control_xml.get(rdf+'ID'), 
                    regulating_control_xml.find(cim+'IdentifiedObject.name').text,
                    regulating_control_xml.find(cim+'RegulatingControl.mode').get(rdf+'resource'),
                    regulating_control_xml.find(cim+'RegulatingControl.Terminal').get(rdf+'resource'),
                    ""))
                for i, regulating_control_xml in zip(range(len(list(self.country_SSH_root.iter(cim+'RegulatingControl')))), self.country_SSH_root.iter(cim+'RegulatingControl')):
                    dic_country[_][i].target_value = regulating_control_xml.find(cim+'RegulatingControl.targetValue').text

            if 'substation_xml' == _:        
                for substation_xml in self.country_EQ_root.iter(cim+"Substation"):
                    dic_country[_].append(Substation(substation_xml.get(rdf+"ID"), 
                    substation_xml.find(cim+"IdentifiedObject.name").text,
                    substation_xml.find(cim+"Substation.Region").get(rdf+"resource")))

            if 'synchronous_machine_xml' == _: 
                for synchronous_machine_xml in self.country_EQ_root.iter(cim+'SynchronousMachine'):
                    dic_country[_].append(SynchronousMachine(synchronous_machine_xml.get(rdf+'ID'), 
                    synchronous_machine_xml.find(cim+'IdentifiedObject.name').text,
                    synchronous_machine_xml.find(cim+'Equipment.EquipmentContainer').get(rdf+'resource'),
                    synchronous_machine_xml.find(cim+'RegulatingCondEq.RegulatingControl').get(rdf+'resource'),
                    synchronous_machine_xml.find(cim+'RotatingMachine.GeneratingUnit').get(rdf+'resource'),
                    "",""))
                
                for i, synchronous_machine_xml in zip(range(len(list(self.country_SSH_root.iter(cim+'SynchronousMachine')))), self.country_SSH_root.iter(cim+'SynchronousMachine')):
                    print(i) 
                    dic_country[_][i].active_power=synchronous_machine_xml.find(cim+"RotatingMachine.p").text
                    dic_country[_][i].reactive_power=synchronous_machine_xml.find(cim+"RotatingMachine.q").text            

            if 'terminal_xml' == _: 

                for terminal_xml in self.country_EQ_root.iter(cim+'Terminal'):
                    dic_country[_].append(Terminal(terminal_xml.get(rdf+'ID'), 
                    terminal_xml.find(cim+'IdentifiedObject.name').text,
                    terminal_xml.find(cim+'Terminal.ConductingEquipment').get(rdf+'resource'),
                    terminal_xml.find(cim+'Terminal.ConnectivityNode').get(rdf+'resource')))

            if 'voltage_level_xml' == _:
                for voltage_level_xml in self.country_EQ_root.iter(cim+'VoltageLevel'):
                    dic_country[_].append(VoltageLevel(voltage_level_xml.get(rdf+'ID'), 
                    voltage_level_xml.find(cim+'IdentifiedObject.name').text,
                    voltage_level_xml.find(cim+'VoltageLevel.Substation').get(rdf+'resource'),
                    voltage_level_xml.find(cim+'VoltageLevel.BaseVoltage').get(rdf+'resource')))
                    
        dic_country

        #Calculation of the reactive power
        def calculate_reactive_power(voltage, susceptance):
            reactive_power = float(voltage)**2 * float(susceptance)
            return reactive_power

        # Function to find busbar depending on the ID of its connectivity node associated
        def find_busbar(cn_ID):
            for _ in range(len(dic_country['terminal_xml'])):
                if '#' + cn_ID == dic_country['terminal_xml'][_].connectivity_node:
                    for i in range(len(dic_country['busbar_section_xml'])):
                        if dic_country['terminal_xml'][_].conducting_equipment == '#' + dic_country['busbar_section_xml'][i].ID:
                            return 'b'
            return 'n'

        # # Create a copy of the dictionary to not affect the mian one, just in case (Safety reasons)
        # dic_country_copy = {key: value.copy() for key, value in dic_country.items()}
        dic_country_copy = dic_country.copy()

        # Update 'voltage_level_xml' IDs
        for voltage_level in dic_country_copy['voltage_level_xml']:
            voltage_level.ID = '#' + voltage_level.ID
            
        # #%%
        # #Create a dictionary for 'voltage_level_xml' based on the updated IDs
        voltage_level_dic = {voltage_level.ID: _ for _, voltage_level in enumerate(dic_country_copy['voltage_level_xml'])}
        voltage_level_dic

        # #Create a dictionary for 'terminal_xml'
        terminal_dic = {'#' + terminal.ID: _ for _, terminal in enumerate(dic_country['terminal_xml'])}
        
        # #Create a dictionary for 'connectivity_node_xml''
        connectivitynode_dict = {}
        for _ in range(len(dic_country_copy['connectivity_node_xml'])):
            connectivitynode_dict['#' + dic_country_copy['connectivity_node_xml'][_].ID] = _
        connectivitynode_dict
        
        ##Transversal Algorithm
        
        # Lines
        container_not_IDs = []
        container_not_IDs2 = []
        not_in_ID = [] 
        # Initializing a 2D list to store information about lines
        AC_line_segment = [[0 for _ in range(4)] for i in range(len(dic_country['AC_line_segment_xml']))]
        # Iteration over the AC line segments
        for _ in range(len(dic_country['AC_line_segment_xml'])):
            AC_line_segment[_][0] = dic_country['AC_line_segment_xml'][_].name
            AC_line_segment[_][3] = float(dic_country['AC_line_segment_xml'][_].length) 
            # Count variable to track the number of terminals associated with the AC line segments
            count = 0
            for i in range(len(dic_country['terminal_xml'])):
                # Checking if the terminal is associated with the current AC line segment
                if  '#' + dic_country['AC_line_segment_xml'][_].ID == dic_country['terminal_xml'][i].conducting_equipment:
                    count += 1
                    # Storing information about the conducting equipment and AC line segment IDs to later check them
                    container_not_IDs.append(dic_country['terminal_xml'][i].conducting_equipment)
                    container_not_IDs2.append('#' + dic_country['AC_line_segment_xml'][_].ID)
                    # Checking if the connectivity node is in the dictionary
                    if dic_country['terminal_xml'][i].connectivity_node in connectivitynode_dict:
                        
                        if count == 1:
                            AC_line_segment[_][1] = connectivitynode_dict[dic_country['terminal_xml'][i].connectivity_node]
                        else:
                            AC_line_segment[_][2] = connectivitynode_dict[dic_country['terminal_xml'][i].connectivity_node]
                    # If the connectivity node is not in the dictionary, add it to the not_in_ID list
                    else:
                        not_in_ID.append(dic_country['terminal_xml'][i].connectivity_node)

        not_in_ID = set(not_in_ID)
        
        #Busbars
        # Initializing a 2D list to store information about Bubsars
        busbar_section = [[0 for _ in range(2)] for i in range(len(dic_country['busbar_section_xml']))]
        # Iteration over  the busbar sections in the counrty
        for _ in range(len(dic_country['busbar_section_xml'])):
            busbar_section[_][0] = dic_country['busbar_section_xml'][_].name 
            # Checking if the current terminal is associated with the current busbar section
            for i in range(len(dic_country['terminal_xml'])):
                if  '#' + dic_country['busbar_section_xml'][_].ID == dic_country['terminal_xml'][i].conducting_equipment:
                    # Getting the connectivity node and voltage level  indices from the dictionary
                    cn = connectivitynode_dict[dic_country['terminal_xml'][i].connectivity_node]
                    voltagelvl = voltage_level_dic[dic_country['connectivity_node_xml'][cn].connectivity_node_container]
                    #Assignation of the voltage level for the busbar section
                    busbar_section[_][1] = float(dic_country_copy['voltage_level_xml'][voltagelvl].name)
        busbar_section
        
        #Breakers
        # Initializing a 2D list to store information about Breakers
        breaker = [[0 for _ in range(4)] for i in range(len(dic_country['breaker_xml']))]
        # Iteration over each breaker
        for _ in range(len(dic_country['breaker_xml'])):
            breaker[_][0] = dic_country['breaker_xml'][_].name
            # Checking the status of the breaker and setting its value in the fourth column of the breaker's information
            if dic_country['breaker_xml'][_].status == 'false':
                breaker[_][3] = True
            # Count variable to keep track of terminals associated with the breakers
            count = 0
            #Finding terminals associated with the current breaker
            for i in range(len(dic_country['terminal_xml'])):
                if  '#' + dic_country['breaker_xml'][_].ID == dic_country['terminal_xml'][i].conducting_equipment:
                    count += 1
                    # Assigning the connectivity node index in the second or third column based on the count variable
                    if count == 1:
                        breaker[_][1] = connectivitynode_dict[dic_country['terminal_xml'][i].connectivity_node]
                    else:
                        breaker[_][2] = connectivitynode_dict[dic_country['terminal_xml'][i].connectivity_node]

        
        #Connectivity Nodes
        # Initializing a 2D list to store information about the connectivity nodes
        connectivity_node = [[0 for _ in range(3)] for i in range(len(dic_country['connectivity_node_xml']))]
        # Iteration over  the connectivity nodes present in the country
        for _ in range(len(dic_country['connectivity_node_xml'])):
            connectivity_node[_][0] = dic_country['connectivity_node_xml'][_].name 
            volt = voltage_level_dic[dic_country['connectivity_node_xml'][_].connectivity_node_container]
            connectivity_node[_][1] = float(dic_country_copy['voltage_level_xml'][volt].name)
            connectivity_node[_][2] = find_busbar(dic_country['connectivity_node_xml'][_].ID)
        # Printing Loop to check the results of the find busbar function
        a = [[0 for _ in range(3)] for j in range(len(dic_country['connectivity_node_xml']))]
        for _ in range(len(dic_country['connectivity_node_xml'])):
            print(find_busbar(dic_country['connectivity_node_xml'][_].ID), _)

        #Generators
        # Iteration over each generating unit and initialization of list 2D for the generating units
        generating_unit = [[0 for _ in range(3)] for i in range(len(dic_country['generating_unit_xml']))]
        for _ in range(len(dic_country['generating_unit_xml'])):
            generating_unit[_][0] = dic_country['generating_unit_xml'][_].name 
            generating_unit[_][2] = float(dic_country['generating_unit_xml'][_].nominalP)
            #A loop to find the terminal associated with the current generating unit
            for i in range(len(dic_country['terminal_xml'])):
                if  '#' + dic_country['generating_unit_xml'][_].ID == dic_country['terminal_xml'][i].conducting_equipment:
                    generating_unit[_][1] = connectivitynode_dict[dic_country['terminal_xml'][i].connectivity_node]
        # Iteration over each synchronous machine and initialization of list 2D for the synchronous machines
        synchronous_machine = [[0 for _ in range(3)] for i in range(len(dic_country['synchronous_machine_xml']))]
        for _ in range(len(dic_country['synchronous_machine_xml'])):
            synchronous_machine[_][0] = dic_country['synchronous_machine_xml'][_].name 
            synchronous_machine[_][2] = float(dic_country['synchronous_machine_xml'][_].active_power)
            #Same loop as done before to find the terminal asscoiated but this time to the current synchronous machine
            for i in range(len(dic_country['terminal_xml'])):
                if  '#' + dic_country['generating_unit_xml'][_].ID == dic_country['terminal_xml'][i].conducting_equipment:
                    generating_unit[_][1] = connectivitynode_dict[dic_country['terminal_xml'][i].connectivity_node]

        #Loads
        # Initializing a 2D list to store information about Enegry consumers
        energy_consumer = [[0 for _ in range(4)] for i in range(len(dic_country['energy_consumer_xml']))]
        for _ in range(len(dic_country['energy_consumer_xml'])):
            #Assigning the name of the load, active power and reactive power in the first, third and fourth columns, respectively
            energy_consumer[_][0] = dic_country['energy_consumer_xml'][_].name 
            energy_consumer[_][2] = float(dic_country['energy_consumer_xml'][_].active_power)
            energy_consumer[_][3] = float(dic_country['energy_consumer_xml'][_].reactive_power) 
            
            # Assigning the connectivity node index in the second column
            for i in range(len(dic_country['terminal_xml'])):
                if  '#' + dic_country['energy_consumer_xml'][_].ID == dic_country['terminal_xml'][i].conducting_equipment:
                    energy_consumer[_][1] = connectivitynode_dict[dic_country['terminal_xml'][i].connectivity_node]

        #Shunt Compensators
        # Iteration over each linear shunt compensator and initialization of list 2D for them
        linear_shunt_compensator = [[0 for _ in range(4)] for i in range(len(dic_country['linear_shunt_compensator_xml']))]
        for _ in range(len(dic_country['linear_shunt_compensator_xml'])):
            linear_shunt_compensator[_][0] = dic_country['linear_shunt_compensator_xml'][_].name 
            linear_shunt_compensator[_][2] = 0
            # Calculating and assigning the reactive power in the third column, by using the previously defined function for Calculation of reactive power
            linear_shunt_compensator[_][3] = float(calculate_reactive_power(dic_country['linear_shunt_compensator_xml'][_].nom_u, dic_country['linear_shunt_compensator_xml'][_].b_per_section)) 
            #Same loop as done before to find the terminal associated, but this time to the current shunt compensator
            for i in range(len(dic_country['terminal_xml'])):
                if  '#' + dic_country['linear_shunt_compensator_xml'][_].ID == dic_country['terminal_xml'][i].conducting_equipment:
                    linear_shunt_compensator[_][1] = connectivitynode_dict[dic_country['terminal_xml'][i].connectivity_node]
        
        #Transformers   
        # Initializing a 2D list to store information about power transformer
        power_transformer = [[0 for _ in range(8)] for i in range(len(dic_country['power_transformer_xml']))]
        # Iteration over power transformers in the country
        for _ in range(len(dic_country['power_transformer_xml'])):
            #Giving the name and type of the power trasnformer in this case "two winding"
            power_transformer[_][0] = dic_country['power_transformer_xml'][_].name
            power_transformer[_][7] = 'two_winding'
            # Initialize lists to store terminal, connectivity node, and voltage level information
            terminal_list = []
            voltagelevel_list = []
            cn_list = []
            # Iteration over power transformer ends to get more information
            for i in range(len(dic_country['power_transformer_end_xml'])):
                # Checking if the power transformer ID matches the power transformer end's attribute
                if  '#' + dic_country['power_transformer_xml'][_].ID == dic_country['power_transformer_end_xml'][i].power_transformer:
                    # Storing the  information found about terminal, connectivity node, and voltage level in the lists previously initialized
                    terminal_list.append(terminal_dic[dic_country['power_transformer_end_xml'][i].terminal])
                    cn_list.append(connectivitynode_dict[dic_country['terminal_xml'][terminal_list[-1]].connectivity_node])
                    voltagelevel_list.append(connectivity_node[cn_list[-1]][1])

            min_voltagelevel_ind = voltagelevel_list.index(min(voltagelevel_list))
            max_voltagelevel_ind = voltagelevel_list.index(max(voltagelevel_list))
            # Assigning information for the primary winding
            power_transformer[_][1] = cn_list[min_voltagelevel_ind]
            power_transformer[_][4] = voltagelevel_list[min_voltagelevel_ind]
            # Assigning information for the secondary winding
            power_transformer[_][3] = cn_list[max_voltagelevel_ind]
            power_transformer[_][6] = voltagelevel_list[max_voltagelevel_ind]
            
            # If there are three windings, assigning information for the tertiary winding
            if len(voltagelevel_list) == 3:
                power_transformer[_][2] = cn_list[3 - (min_voltagelevel_ind + max_voltagelevel_ind)]
                power_transformer[_][5] = voltagelevel_list[3 - (min_voltagelevel_ind + max_voltagelevel_ind)]
                power_transformer[_][7] = 'three_winding'

        ### Pandapower
        net = pp.create_empty_network()

        #Creating the busbars in the pandapower network
        for _ in range (len(dic_country['connectivity_node_xml'])):
            pp.create_bus (net, name=connectivity_node[_][0], vn_kv=connectivity_node[_][1], type = connectivity_node[_][2])
        print('\n','Busbars')  
        print(net.bus)

        #Creating the Lines in the pandapower network
        for _ in range (len(dic_country['AC_line_segment_xml'])):
            pp.create_line(net, AC_line_segment[_][1], AC_line_segment[_][2], length_km = AC_line_segment[_][3], std_type = "N2XS(FL)2Y 1x300 RM/35 64/110 kV",  name = AC_line_segment[_][0])

        print('\n','Lines')  
        print(net.line)
        
        #Creating the Breakers in the pandapower network
        for _ in range (len(dic_country['breaker_xml'])):
            pp.create_switch(net, breaker[_][1], breaker[_][2], et="b", type="CB", closed = breaker[_][3])

        print('\n','Breakers')  
        print(net.switch)
        
        #Creating the Generators in the pandapower network
        for _ in range (len(dic_country['generating_unit_xml'])):
            pp.create_sgen(net, generating_unit[_][1], p_mw = generating_unit[_][2], name = generating_unit[_][0])
        print('\n','Generators') 
        print(net.sgen)
        
        #Creating the Loads in the pandapower network
        for _ in range (len(dic_country['energy_consumer_xml'])):
            pp.create_load(net, energy_consumer[_][1], p_mw = energy_consumer[_][2], q_mvar = energy_consumer[_][3], name = energy_consumer[_][0])
        print('\n','Loads')  
        print(net.load)
        
        #Creating the Shunt Compensators in the pandapower network
        for _ in range(len(dic_country['linear_shunt_compensator_xml'])):
            pp.create.create_shunt(net, linear_shunt_compensator[_][1], q_mvar=linear_shunt_compensator[_][3] , p_mw=0)
        print('\n','Compensators') 
        print(net.shunt)
        
        #Creating the Transformers in the pandapower network
        for _ in range (len(dic_country['power_transformer_xml'])):
            if power_transformer[_][7] == 'two_winding':
                pp.create_transformer (net, power_transformer[_][3], power_transformer[_][1], name = power_transformer[_][0], std_type="25 MVA 110/20 kV")
            if power_transformer[_][7] == 'three_winding':
                pp.create.create_transformer3w (net, power_transformer[_][3], power_transformer[_][2], power_transformer[_][1], name = power_transformer[_][0], std_type="63/25/38 MVA 110/20/10 kV")
        # print('\n','Transformers')  
        # print(net.transformer)
        
        terminal_country_merge = {}
        for _ in range(len(dic_country['terminal_xml'])):
            terminal_country_merge['#' + dic_country['terminal_xml'][_].ID, dic_country['terminal_xml'][_].connectivity_node] = _
        terminal_country_merge
        return(net, dic_country, not_in_ID, connectivitynode_dict, busbar_section, AC_line_segment)

    def maestro_chart(net):
         
        pp.plotting.simple_plot(net, respect_switches=True, line_width=1.0, bus_size=1.0, ext_grid_size=1.0, trafo_size=1.0, plot_loads=True, plot_gens=True, plot_sgens=True, load_size=1.0, gen_size=1.0, sgen_size=1.0, switch_size=2.0, switch_distance=1.0, plot_line_switches=True, scale_size=True, bus_color='b', line_color='grey', dcline_color='c', trafo_color='k', ext_grid_color='y', switch_color='k', library='igraph', show_plot=True, ax=None)
        # pp.plotting.plotly.simple_plotly(net, respect_switches=True, use_line_geodata=None, on_map=True, projection=None, map_style='basic', figsize=1.0, aspectratio='auto', line_width=1.0, bus_size=10.0, ext_grid_size=20.0, bus_color='blue', line_color='grey', trafo_color='green', trafo3w_color='green', ext_grid_color='yellow', filename='temp-plot.html', auto_open=True, showlegend=True, additional_traces=None)

# %%
#Parsing EQ files for each country
be_EQ_tree = ET.parse('MicroGridTestConfiguration_T3_BE_EQ_V2.xml')
nl_EQ_tree = ET.parse('MicroGridTestConfiguration_T3_NL_EQ_V2.xml')

# %%
#Parsing SSH files for each country
be_SSH_tree = ET.parse('MicroGridTestConfiguration_T3_BE_SSH_V2.xml')
nl_SSH_tree = ET.parse('MicroGridTestConfiguration_T3_NL_SSH_V2.xml')


# %%
#Storing namespace identifiers in strings to use them when a tag is searched
cim = "{http://iec.ch/TC57/2013/CIM-schema-cim16#}"
rdf = "{http://www.w3.org/1999/02/22-rdf-syntax-ns#}"
md = "{http://www.w3.org/1999/02/22-rdf-syntax-ns#}"

# %%
#Results of the code done above for Belgium
df_be = maestro(be_EQ_tree, be_SSH_tree, cim, rdf, md)
net_be, dic_be, not_in_ID_be, connectivitynode_dict_be, busbar_section_be, AC_line_segment_be = df_be.xml_extraction()
maestro.maestro_chart(net_be)
# %%
#Results of the code done above for Netherlands
df_nl = maestro(nl_EQ_tree, nl_SSH_tree, cim, rdf, md)
net_nl, dic_nl, not_in_ID_nl, connectivitynode_dict_nl, busbar_section_nl, AC_line_segment_nl= df_nl.xml_extraction()
maestro.maestro_chart(net_nl)
# %%
#List of the IDs that are present in both countries' files
common_IDs= list(set(not_in_ID_be).intersection(not_in_ID_nl))
print('\n','Common IDs in both countries') 
for common_id in common_IDs:
    print(common_id)
    
#%%
#Merge
# Interconnecting the lines using a switch
# switch_element = pp.create_switch(net_be, bus=net_be.bus[0][1], element="_17086487-56ba-4979-b8de-064025a6b4da", et="l", closed=True)
# pp.create_switch(net_nl, bus="_12733133-1f34-44f3-a020-f5b33cede919", element="_8fdc7abd-3746-481a-a65e-3df56acd8b13", et="l", closed=True)

# Merging the two networks
# pp.merge_nets(net_be, net_nl)

# Check the final network structure
# maestro.maestro_chart(net_be)



#%%
# class maestro_merge:

#     def __init__(self, dic_be, dic_nl):

#         self.dic_be = dic_be
#         self.dic_nl = dic_nl   

#     def ID_identifier(dic_country):
#         list_keys = dic_country.keys()
        
#         ID_container = {}
#         ID_container_list = []

#         for _ in list_keys:
#             n_elements = len(dic_country[_])

#             for i in range(n_elements):
#                 ID_container_list.append(dic_country[_][i].ID)
            
#             ID_container[_] =  ID_container_list
#             ID_container_list = []
        
#         return(ID_container)
    
#     def ID_merge(ID_container_be, ID_container_nl):

#         ID_container_in_both = {}
#         ID_container_list_be = []
#         ID_container_list_nl = []

#         list_keys = ID_container_be.keys()

#         for _ in list_keys:
#             n_elements_be = len(ID_container_be[_])
#             n_elements_nl = len(ID_container_nl[_])

#             for i in range(n_elements_be):
#                 ID_container_list_be.append(ID_container_be[_][i])

#             for j in range(n_elements_nl):
#                 ID_container_list_nl.append(ID_container_nl[_][j])
            
#             ID_container_in_both[_] = list(set(ID_container_list_be).intersection(ID_container_list_nl))

#             ID_container_list_be = []
        
#             ID_container_list_nl = []
        
#         return(ID_container_in_both)
#%%
# line_IDs_to_interconnect_be = ["_17086487-56ba-4979-b8de-064025a6b4da", "_78736387-5f60-4832-b3fe-d50daf81b0a6", "_ed0c5d75-4a54-43c8-b782-b20d7431630b", "_b18cd1aa-7808-49b9-a7cf-605eaf07b006", "_a16b4a6c-70b1-4abf-9a9d-bd0fa47f9fe4"]
# line_IDs_to_interconnect_nl = ["_8fdc7abd-3746-481a-a65e-3df56acd8b13", "_7f43f508-2496-4b64-9146-0a40406cbe49", "_dad02278-bd25-476f-8f58-dbe44be72586", "_e8acf6b6-99cb-45ad-b8dc-16c7866a4ddc", "_a279a3dc-550b-426c-af3a-61b7be508dcc"]

# bus_IDs_to_interconnect_be = ["_64901aec-5a8a-4bcb-8ca7-a3ddbfcd0e6c", ""]
# bus_IDs_to_interconnect_nl = ["_12733133-1f34-44f3-a020-f5b33cede919"]

# # Interconnect the lines using switches
# for line_id_be, line_id_nl in zip(line_IDs_to_interconnect_be, line_IDs_to_interconnect_nl):
#     switch_element = pp.create_switch(net_be, bus=bus_IDs_to_interconnect_be, element=line_id_be, et="l", closed=True)
#     pp.create_switch(net_nl, bus=bus_IDs_to_interconnect_nl, element=line_id_nl, et="l", closed=True)
    
# # Merge the two networks
# pp.merge_nets(net_be, net_nl)
# maestro.maestro_chart(net_be)


# #%%
# ID_container_be = maestro_merge.ID_identifier(dic_be)
# ID_container_nl = maestro_merge.ID_identifier(dic_nl)
# #%%
# ID_container_in_both = maestro_merge.ID_merge(ID_container_be, ID_container_nl)
# ID_container_in_both
# #%%
# # Merge
# container_not_IDs3 = []
# container_not_IDs4 = []

# AC_line_segment = [[0 for _ in range(4)] for i in range(len(dic_be['AC_line_segment_xml']))]
# for _ in range(len(dic_be['AC_line_segment_xml'])):
#     AC_line_segment[_][0] = dic_be['AC_line_segment_xml'][_].name
#     AC_line_segment[_][3] = float(dic_be['AC_line_segment_xml'][_].length) 

#     count = 0
#     for i in range(len(dic_nl['terminal_xml'])):

#         if  '#' + dic_be['AC_line_segment_xml'][_].ID == dic_nl['terminal_xml'][i].conducting_equipment:
#             count += 1
#             container_not_IDs3.append(dic_nl['terminal_xml'][i].conducting_equipment)
#             container_not_IDs4.append('#' + dic_be['AC_line_segment_xml'][_].ID)
#             if dic_nl['terminal_xml'][i].connectivity_node in connectivitynode_dict_be:
                
#                 if count == 1:
#                     AC_line_segment[_][1] = connectivitynode_dict_nl[dic_nl['terminal_xml'][i].connectivity_node]
#                 else:
#                     AC_line_segment[_][2] = connectivitynode_dict_nl[dic_nl['terminal_xml'][i].connectivity_node]

# AC_line_segment
# # dic_country['terminal_xml'][i].connectivity_node
# #%%
# AC_line_segment_be
# #%%
# AC_line_segment_nl
# #%%
# # Example usage Belgium

# # common_cn_id = "#_b6978550-cb6e-11e1-bcee-406c8f32ef58"
# #Belgium
# ## Terminal rdf:ID="_4a7363a4-0b21-4f65-8bba-33e3a8f6bac3">
# # im:IdentifiedObject.name>BE-Inj-XZE_ST24 - T1</cim:IdentifiedObject.name>
# # ntsoe:IdentifiedObject.shortName>BE-I-XZE_ST2</entsoe:IdentifiedObject.shortName>
# # im:ACDCTerminal.sequenceNumber>1</cim:ACDCTerminal.sequenceNumber>
# # im:Terminal.phases rdf:resource="http://iec.ch/TC57/2013/CIM-schema-cim16#PhaseCode.ABC"/>
# # im:Terminal.ConductingEquipment rdf:resource="#_f7f61a91-eca2-4492-8bd7-9ec2b28fc837"/>
# # im:Terminal.ConnectivityNode rdf:resource="#_b6978550-cb6e-11e1-bcee-406c8f32ef58"/>
# ## Terminal rdf:ID="_57ae9251-c022-4c67-a8eb-611ad54c963c">
# # im:IdentifiedObject.name>BE-Line_7 - T1</cim:IdentifiedObject.name>
# # ntsoe:IdentifiedObject.shortName>BE-L_7</entsoe:IdentifiedObject.shortName>
# # im:ACDCTerminal.sequenceNumber>1</cim:ACDCTerminal.sequenceNumber>
# # im:Terminal.phases rdf:resource="http://iec.ch/TC57/2013/CIM-schema-cim16#PhaseCode.ABC"/>
# # im:Terminal.ConductingEquipment rdf:resource="#_a16b4a6c-70b1-4abf-9a9d-bd0fa47f9fe4"/>
# # im:Terminal.ConnectivityNode rdf:resource="#_b6978550-cb6e-11e1-bcee-406c8f32ef58"/>
# # ntsoe:IdentifiedObject.energyIdentCodeEic>10T-AT-DE-000061</entsoe:IdentifiedObject.energyIdentCodeEic>
# #Netherlands
# ## Terminal rdf:ID="_26e50b4b-9a19-420d-98ce-bc4f11971cd7">
# # im:IdentifiedObject.name>NL-Inj-XZE_ST24 - T1</cim:IdentifiedObject.name>
# # ntsoe:IdentifiedObject.shortName>NL-I-XZE_ST2</entsoe:IdentifiedObject.shortName>
# # im:ACDCTerminal.sequenceNumber>1</cim:ACDCTerminal.sequenceNumber>
# # im:Terminal.phases rdf:resource="http://iec.ch/TC57/2013/CIM-schema-cim16#PhaseCode.ABC"/>
# # im:Terminal.ConductingEquipment rdf:resource="#_820d95d7-26d4-4311-8b1f-026f8605b86d"/>
# # im:Terminal.ConnectivityNode rdf:resource="#_b6978550-cb6e-11e1-bcee-406c8f32ef58"/>
# ## Terminal rdf:ID="_9dd1915f-dd54-407d-a735-fb4ea99c9ca2">
# # im:IdentifiedObject.name>NL-Line_5 - T1</cim:IdentifiedObject.name>
# # ntsoe:IdentifiedObject.shortName>NL-L_3</entsoe:IdentifiedObject.shortName>
# # im:ACDCTerminal.sequenceNumber>1</cim:ACDCTerminal.sequenceNumber>
# # im:Terminal.phases rdf:resource="http://iec.ch/TC57/2013/CIM-schema-cim16#PhaseCode.ABC"/>
# # im:Terminal.ConductingEquipment rdf:resource="#_a279a3dc-550b-426c-af3a-61b7be508dcc"/>
# # im:Terminal.ConnectivityNode rdf:resource="#_b6978550-cb6e-11e1-bcee-406c8f32ef58"/>
# # ntsoe:IdentifiedObject.energyIdentCodeEic>10T-AT-DE-00009W</entsoe:IdentifiedObject.energyIdentCodeEic>

# #Para este primer ID se conectan las líneas NL-Line_3 y BE-Line_7
# Line segment ID = "_a279a3dc-550b-426c-af3a-61b7be508dcc" Netherlands
# Line segment ID = "_a16b4a6c-70b1-4abf-9a9d-bd0fa47f9fe4" Belgium



# # common_cn_id = '#_b67c8340-cb6e-11e1-bcee-406c8f32ef58'
# #Belgium
# ## Terminal rdf:ID="_02a244ca-8bcb-4e25-8613-e948b8ba1f22">
# # im:IdentifiedObject.name>BE-Line_5 - T2</cim:IdentifiedObject.name>
# # ntsoe:IdentifiedObject.shortName>BE-L_5</entsoe:IdentifiedObject.shortName>
# # im:ACDCTerminal.sequenceNumber>2</cim:ACDCTerminal.sequenceNumber>
# # im:Terminal.phases rdf:resource="http://iec.ch/TC57/2013/CIM-schema-cim16#PhaseCode.ABC"/>
# # im:Terminal.ConductingEquipment rdf:resource="#_b18cd1aa-7808-49b9-a7cf-605eaf07b006"/>
# # im:Terminal.ConnectivityNode rdf:resource="#_b67c8340-cb6e-11e1-bcee-406c8f32ef58"/>
# # ntsoe:IdentifiedObject.energyIdentCodeEic>10T-AT-DE-00009W</entsoe:IdentifiedObject.energyIdentCodeEic>
# ## Terminal rdf:ID="_b9539c41-d114-4280-8a54-8ecec398091e">
# # im:IdentifiedObject.name>BE-Inj-XWI_GY11 - T1</cim:IdentifiedObject.name>
# # ntsoe:IdentifiedObject.shortName>BE-I-XWI_GY1</entsoe:IdentifiedObject.shortName>
# # im:ACDCTerminal.sequenceNumber>1</cim:ACDCTerminal.sequenceNumber>
# # im:Terminal.phases rdf:resource="http://iec.ch/TC57/2013/CIM-schema-cim16#PhaseCode.ABC"/>
# # im:Terminal.ConductingEquipment rdf:resource="#_6f014d4c-c1b0-4eed-8d6d-bae3bc87afcf"/>
# # im:Terminal.ConnectivityNode rdf:resource="#_b67c8340-cb6e-11e1-bcee-406c8f32ef58"/>
# #Netherlands
# ## Terminal rdf:ID="_ae588863-b154-451d-978a-7ab08ac50fb6">
# # im:IdentifiedObject.name>NL-Line_5 - T2</cim:IdentifiedObject.name>
# # ntsoe:IdentifiedObject.shortName>NL-L_5</entsoe:IdentifiedObject.shortName>
# # im:ACDCTerminal.sequenceNumber>2</cim:ACDCTerminal.sequenceNumber>
# # im:Terminal.phases rdf:resource="http://iec.ch/TC57/2013/CIM-schema-cim16#PhaseCode.ABC"/>
# # im:Terminal.ConductingEquipment rdf:resource="#_e8acf6b6-99cb-45ad-b8dc-16c7866a4ddc"/>
# # im:Terminal.ConnectivityNode rdf:resource="#_b67c8340-cb6e-11e1-bcee-406c8f32ef58"/>
# # ntsoe:IdentifiedObject.energyIdentCodeEic>10T-AT-DE-000118</entsoe:IdentifiedObject.energyIdentCodeEic>
# ## Terminal rdf:ID="_f48d48c7-e9f6-460c-898f-cc68a96efdeb">
# # im:IdentifiedObject.name>NL-Inj-XWI_GY11 - T1</cim:IdentifiedObject.name>
# # ntsoe:IdentifiedObject.shortName>NL-I-XWI_GY1</entsoe:IdentifiedObject.shortName>
# # im:ACDCTerminal.sequenceNumber>1</cim:ACDCTerminal.sequenceNumber>
# # im:Terminal.phases rdf:resource="http://iec.ch/TC57/2013/CIM-schema-cim16#PhaseCode.ABC"/>
# # im:Terminal.ConductingEquipment rdf:resource="#_b0442899-8dbe-48c1-a1fa-adb2a5929273"/>
# # im:Terminal.ConnectivityNode rdf:resource="#_b67c8340-cb6e-11e1-bcee-406c8f32ef58"/>

# #Para este primer ID se conectan las líneas NL-Line_5 y BE-Line_5
# Line segment ID = "_e8acf6b6-99cb-45ad-b8dc-16c7866a4ddc" Netherlands
# Line segment ID = "_b18cd1aa-7808-49b9-a7cf-605eaf07b006" Belgium

# # common_cn_id = "#_b67cf870-cb6e-11e1-bcee-406c8f32ef58"
# #Belgium
# ## Terminal rdf:ID="_c41978db-794b-4bae-953e-60fc519e87dd">
# # im:IdentifiedObject.name>BE-Inj-XKA_MA11 - T1</cim:IdentifiedObject.name>
# # ntsoe:IdentifiedObject.shortName>BE-I-XKA_MA1</entsoe:IdentifiedObject.shortName>
# # im:ACDCTerminal.sequenceNumber>1</cim:ACDCTerminal.sequenceNumber>
# # im:Terminal.phases rdf:resource="http://iec.ch/TC57/2013/CIM-schema-cim16#PhaseCode.ABC"/>
# # im:Terminal.ConductingEquipment rdf:resource="#_14b352cb-5574-40c5-bf83-0ed3574554a3"/>
# # im:Terminal.ConnectivityNode rdf:resource="#_b67cf870-cb6e-11e1-bcee-406c8f32ef58"/>
# ## Terminal rdf:ID="_f9f29835-8a31-4310-9780-b1ad26f3cbb0">
# # im:IdentifiedObject.name>BE-Line_4 - T2</cim:IdentifiedObject.name>
# # ntsoe:IdentifiedObject.shortName>BE-L_4</entsoe:IdentifiedObject.shortName>
# # im:ACDCTerminal.sequenceNumber>2</cim:ACDCTerminal.sequenceNumber>
# # im:Terminal.phases rdf:resource="http://iec.ch/TC57/2013/CIM-schema-cim16#PhaseCode.ABC"/>
# # im:Terminal.ConductingEquipment rdf:resource="#_ed0c5d75-4a54-43c8-b782-b20d7431630b"/>
# # im:Terminal.ConnectivityNode rdf:resource="#_b67cf870-cb6e-11e1-bcee-406c8f32ef58"/>
# #Netherlands
# ## Terminal rdf:ID="_8f308117-8bbd-4798-b145-4e78f7d049e7">
# # im:IdentifiedObject.name>NL-Line_2 - T2</cim:IdentifiedObject.name>
# # ntsoe:IdentifiedObject.shortName>NL-L_2</entsoe:IdentifiedObject.shortName>
# # im:ACDCTerminal.sequenceNumber>2</cim:ACDCTerminal.sequenceNumber>
# # im:Terminal.phases rdf:resource="http://iec.ch/TC57/2013/CIM-schema-cim16#PhaseCode.ABC"/>
# # im:Terminal.ConductingEquipment rdf:resource="#_dad02278-bd25-476f-8f58-dbe44be72586"/>
# # im:Terminal.ConnectivityNode rdf:resource="#_b67cf870-cb6e-11e1-bcee-406c8f32ef58"/>
# ## Terminal rdf:ID="_f970233f-b573-49d9-9fc3-3a2a59ed3bbb">
# # im:IdentifiedObject.name>NL-Inj-XKA_MA11 - T1</cim:IdentifiedObject.name>
# # ntsoe:IdentifiedObject.shortName>NL-I-XKA_MA1</entsoe:IdentifiedObject.shortName>
# # im:ACDCTerminal.sequenceNumber>1</cim:ACDCTerminal.sequenceNumber>
# # im:Terminal.phases rdf:resource="http://iec.ch/TC57/2013/CIM-schema-cim16#PhaseCode.ABC"/>
# # im:Terminal.ConductingEquipment rdf:resource="#_cab82e1c-1435-447b-bba0-74b592539eac"/>
# # im:Terminal.ConnectivityNode rdf:resource="#_b67cf870-cb6e-11e1-bcee-406c8f32ef58"/>

# #Para este primer ID se conectan las líneas NL-Line_2 y BE-Line_4
# Line segment ID = "_dad02278-bd25-476f-8f58-dbe44be72586" Netherlands
# Line segment ID = "_ed0c5d75-4a54-43c8-b782-b20d7431630b" Belgium

# # common_cn_id = "#_b675a570-cb6e-11e1-bcee-406c8f32ef58"
# #Belgium
# ## Terminal rdf:ID="_53072f42-f77b-47e2-bd9a-e097c910b173">
# # im:IdentifiedObject.name>BE-Inj-XCA_AL11 - T1</cim:IdentifiedObject.name>
# # ntsoe:IdentifiedObject.shortName>BE-I-XCA_AL1</entsoe:IdentifiedObject.shortName>
# # im:ACDCTerminal.sequenceNumber>1</cim:ACDCTerminal.sequenceNumber>
# # im:Terminal.phases rdf:resource="http://iec.ch/TC57/2013/CIM-schema-cim16#PhaseCode.ABC"/>
# # im:Terminal.ConductingEquipment rdf:resource="#_24413233-26c3-4f7e-9f72-4461796938be"/>
# # im:Terminal.ConnectivityNode rdf:resource="#_b675a570-cb6e-11e1-bcee-406c8f32ef58"/>
# ## Terminal rdf:ID="_f3b56334-4638-49d3-a6a0-3f417422b8f5">
# # im:IdentifiedObject.name>BE-Line_3 - T2</cim:IdentifiedObject.name>
# # ntsoe:IdentifiedObject.shortName>BE-L_3</entsoe:IdentifiedObject.shortName>
# # im:ACDCTerminal.sequenceNumber>2</cim:ACDCTerminal.sequenceNumber>
# # im:Terminal.phases rdf:resource="http://iec.ch/TC57/2013/CIM-schema-cim16#PhaseCode.ABC"/>
# # im:Terminal.ConductingEquipment rdf:resource="#_78736387-5f60-4832-b3fe-d50daf81b0a6"/>
# # im:Terminal.ConnectivityNode rdf:resource="#_b675a570-cb6e-11e1-bcee-406c8f32ef58"/>
# # ntsoe:IdentifiedObject.energyIdentCodeEic>10T-AT-DE-00008Y</entsoe:IdentifiedObject.energyIdentCodeEic>
# #Netherlands
# ## Terminal rdf:ID="_6b1cd30c-19ba-44e1-9447-d01db6b1ef9d">
# # im:IdentifiedObject.name>NL-Line_1 - T2</cim:IdentifiedObject.name>
# # ntsoe:IdentifiedObject.shortName>NL-L_1</entsoe:IdentifiedObject.shortName>
# # im:ACDCTerminal.sequenceNumber>2</cim:ACDCTerminal.sequenceNumber>
# # im:Terminal.phases rdf:resource="http://iec.ch/TC57/2013/CIM-schema-cim16#PhaseCode.ABC"/>
# # im:Terminal.ConductingEquipment rdf:resource="#_7f43f508-2496-4b64-9146-0a40406cbe49"/>
# # im:Terminal.ConnectivityNode rdf:resource="#_b675a570-cb6e-11e1-bcee-406c8f32ef58"/>
# # ntsoe:IdentifiedObject.energyIdentCodeEic>10T-AT-DE-000118</entsoe:IdentifiedObject.energyIdentCodeEic>
# ## Terminal rdf:ID="_39d27c17-1e5b-4edc-a7ec-65a2d56542df">
# # im:IdentifiedObject.name>NL-Inj-XCA_AL11 - T1</cim:IdentifiedObject.name>
# # ntsoe:IdentifiedObject.shortName>NL-I-XCA_AL1</entsoe:IdentifiedObject.shortName>
# # im:ACDCTerminal.sequenceNumber>1</cim:ACDCTerminal.sequenceNumber>
# # im:Terminal.phases rdf:resource="http://iec.ch/TC57/2013/CIM-schema-cim16#PhaseCode.ABC"/>
# # im:Terminal.ConductingEquipment rdf:resource="#_83bea592-913e-4473-8d17-969968ff83a2"/>
# # im:Terminal.ConnectivityNode rdf:resource="#_b675a570-cb6e-11e1-bcee-406c8f32ef58"/>

# #Para este primer ID se conectan las líneas NL-Line_1 y BE-Line_3
# Line segment ID = "_7f43f508-2496-4b64-9146-0a40406cbe49" Netherlands
# Line segment ID = "_78736387-5f60-4832-b3fe-d50daf81b0a6" Belgium

# # common_cn_id = "#_b66f15c0-cb6e-11e1-bcee-406c8f32ef58"
# #Belgium
# ## Terminal rdf:ID="_d238885e-d9b6-4edc-8567-6a68c605ed67">
# # im:IdentifiedObject.name>BE-Inj-XZE_ST23 - T1</cim:IdentifiedObject.name>
# # ntsoe:IdentifiedObject.shortName>BE-I-XZE_ST2</entsoe:IdentifiedObject.shortName>
# # im:ACDCTerminal.sequenceNumber>1</cim:ACDCTerminal.sequenceNumber>
# # im:Terminal.phases rdf:resource="http://iec.ch/TC57/2013/CIM-schema-cim16#PhaseCode.ABC"/>
# # im:Terminal.ConductingEquipment rdf:resource="#_87ea56f3-962a-427a-85d6-13b1f9295174"/>
# # im:Terminal.ConnectivityNode rdf:resource="#_b66f15c0-cb6e-11e1-bcee-406c8f32ef58"/>
# ## Terminal rdf:ID="_1ef0715a-d5a9-477b-b6e7-b635529ac140">
# # im:IdentifiedObject.name>BE-Line_1 - T1</cim:IdentifiedObject.name>
# # ntsoe:IdentifiedObject.shortName>BE-L_1</entsoe:IdentifiedObject.shortName>
# # im:ACDCTerminal.sequenceNumber>1</cim:ACDCTerminal.sequenceNumber>
# # im:Terminal.phases rdf:resource="http://iec.ch/TC57/2013/CIM-schema-cim16#PhaseCode.ABC"/>
# # im:Terminal.ConductingEquipment rdf:resource="#_17086487-56ba-4979-b8de-064025a6b4da"/>
# # im:Terminal.ConnectivityNode rdf:resource="#_b66f15c0-cb6e-11e1-bcee-406c8f32ef58"/>
# # ntsoe:IdentifiedObject.energyIdentCodeEic>10T-AT-DE-000061</entsoe:IdentifiedObject.energyIdentCodeEic>
# #Netherlands
# ## Terminal rdf:ID="_24dd035c-0a8c-4351-aeb2-08d6622b42ae">
# # im:IdentifiedObject.name>NL-Inj-XZE_ST23 - T1</cim:IdentifiedObject.name>
# # ntsoe:IdentifiedObject.shortName>NL-I-XZE_ST2</entsoe:IdentifiedObject.shortName>
# # im:ACDCTerminal.sequenceNumber>1</cim:ACDCTerminal.sequenceNumber>
# # im:Terminal.phases rdf:resource="http://iec.ch/TC57/2013/CIM-schema-cim16#PhaseCode.ABC"/>
# # im:Terminal.ConductingEquipment rdf:resource="#_12baa3f3-23b1-44e0-956f-d331e1527f37"/>
# # im:Terminal.ConnectivityNode rdf:resource="#_b66f15c0-cb6e-11e1-bcee-406c8f32ef58"/>
# ## Terminal rdf:ID="_57979d14-d1d8-4311-ae53-aa8890423885">
# # im:IdentifiedObject.name>NL-Line_4 - T2</cim:IdentifiedObject.name>
# # ntsoe:IdentifiedObject.shortName>NL-L_4</entsoe:IdentifiedObject.shortName>
# # im:ACDCTerminal.sequenceNumber>2</cim:ACDCTerminal.sequenceNumber>
# # im:Terminal.phases rdf:resource="http://iec.ch/TC57/2013/CIM-schema-cim16#PhaseCode.ABC"/>
# # im:Terminal.ConductingEquipment rdf:resource="#_8fdc7abd-3746-481a-a65e-3df56acd8b13"/>
# # im:Terminal.ConnectivityNode rdf:resource="#_b66f15c0-cb6e-11e1-bcee-406c8f32ef58"/>
# # ntsoe:IdentifiedObject.energyIdentCodeEic>10T-AT-DE-00009W</entsoe:IdentifiedObject.energyIdentCodeEic>

# #Para este primer ID se conectan las líneas NL-Line_4 y BE-Line_1
# Line segment ID = "_8fdc7abd-3746-481a-a65e-3df56acd8b13" Netherlands
# Line segment ID = "_17086487-56ba-4979-b8de-064025a6b4da" Belgium

print('\n','The lines which should have been connected to have the merge working were found by analizing the xml files') 
print('\n','For the common connectivity ID  "#_b66f15c0-cb6e-11e1-bcee-406c8f32ef58" , the two lines that must be connected to eachother are : NL-Line_4 and BE-Line_1')
print('\n','For the common connectivity ID  "#_b675a570-cb6e-11e1-bcee-406c8f32ef58" , the two lines that must be connected to eachother are : NL-Line_1 and BE-Line_3')
print('\n','For the common connectivity ID  "#_b67cf870-cb6e-11e1-bcee-406c8f32ef58" , the two lines that must be connected to eachother are : NL-Line_2 and BE-Line_4')
print('\n','For the common connectivity ID  "#_b67c8340-cb6e-11e1-bcee-406c8f32ef58" , the two lines that must be connected to eachother are : NL-Line_5 and BE-Line_5')
print('\n','For the common connectivity ID  "#_b6978550-cb6e-11e1-bcee-406c8f32ef58" , the two lines that must be connected to eachother are : NL-Line_3 and BE-Line_7')

