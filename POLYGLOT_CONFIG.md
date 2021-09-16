# Universal Devices BAS Pool Controller

## BASpi-SYS6U6R DIY BacNet Control Device by Contemporary Controls

### This Nodeserver is for custom control of BASpi modules on an IP Network network

* The purpose of this Nodeserver is for Pool Control and home automation using BASpi modules on an IP network.
* Python 3.7.7

* Supported Nodes
  * Inputs
  * Outputs

#### Configuration

##### Defaults

* Default Short Poll:  Every 2 minutes
* Default Long Poll: Every 4 minutes

###### User Provided

* Enter the number of pool nodes you desire 0-5
* Enter your IP address for up to six (6) BASpi-SYS6U6R controller,
* Config: key = poolip_* (* = 0-5) this parameter is provided, Value = Enter Your BASpi IP Address, Example: key poolip_0  value 192.168.1.47
* Save and restart the NodeServer
  