from dcim.choices import DeviceStatusChoices
from dcim.models import Device, DeviceType, Interface
from extras.reports import Report
from collections import Counter


class DeviceAndTemplate(Report):
    description = "Check for differences in the template and corresponding devices"

    def test_count_interfaces(self):

        active = DeviceStatusChoices.STATUS_ACTIVE
        planned = DeviceStatusChoices.STATUS_PLANNED

        for device in Device.objects.filter(status__in=[active, planned]):

            # get device physical interface count
            device_interface_count = len([ i['id'] for i in device.interfaces.exclude(type__in=["virtual", "lag"]).values()])

            # get device template interface count
            device_template_interface_count = DeviceType.objects.filter(id = device.device_type_id)[0].interface_templates.exclude(type__in=["virtual", "lag"]).count()

            if device_interface_count != device_template_interface_count:
                self.log_warning(
                    device,
                    device.device_type.display_name + " has  " + str(device_template_interface_count) + ", " + device.name + " has " + str(device_interface_count)
                )
            else:
                self.log_success(
                    device
                )

    def test_interface_name(self):

        active = DeviceStatusChoices.STATUS_ACTIVE
        planned = DeviceStatusChoices.STATUS_PLANNED

        for device in Device.objects.filter(status__in=[active, planned]):

           # get all physical device interfaces names
           device_interface_names = [inf['name'] for inf in device.interfaces.exclude(type__in=["virtual", "lag"]).values()]

           # get device template
           device_template = DeviceType.objects.filter(id = device.device_type_id)[0]

           # get all device template interfaces names
           template_interface_names = [inf['name'] for inf in device_template.interface_templates.exclude(type__in=["virtual", "lag"]).values()]

           if device_interface_names == template_interface_names:
               self.log_success(
                   device
               )
           else:
               missing_device_ints = list(set(device_interface_names).difference(template_interface_names))
               missing_devicetype_ints = list(set(template_interface_names).difference(device_interface_names))

               if len(missing_device_ints) > 0:
                   self.log_warning(
                       device,
                       "Interfaces on Device NOT on the DeviceType: " + str(missing_device_ints)
                   )

               if len(missing_devicetype_ints) > 0:
                   self.log_warning(
                       device,
                       "Interfaces on DeviceType NOT on the Device: " + str(missing_devicetype_ints)
                   )


class InterfaceConnection(Report):
    description = "Check for physical interface connections that are not connected"

    def test_interface_connection(self):
        active = DeviceStatusChoices.STATUS_ACTIVE
        planned = DeviceStatusChoices.STATUS_PLANNED
        for device in Device.objects.filter(status__in=[active, planned]):
            # get list with all physical device interfaces
            device_interfaces = [ inf['id'] for inf in device.interfaces.exclude(type__in=["virtual", "lag"]).values() ]

            # if exist physical interfaces -> check it, else not exist -> success
            if device_interfaces:
                inf_not_connected = []

                for inf_id in device_interfaces:
                    # get interface object
                    inf = Interface.objects.filter(id = inf_id)[0]
                    # if interface not connected add to list
                    if not inf.connection_status:
                        inf_not_connected.append(inf.name)

                # if exist not connected interfaces -> warning, else -> success
                if inf_not_connected:
                    self.log_warning(
                        device,
                        "Not connected interfaces: {}".format(inf_not_connected)
                    )
                else:
                    self.log_success(
                        device
                    )
            else:
                self.log_success(
                    device
                )
