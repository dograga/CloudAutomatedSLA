# CloudAutomatedSLA

Cloud Automation SLA script to update uptime of cloud management service. Periodic check of Cloud component including:

1. Custom Cloud Layer
2. Cloudstack
3. Vcenter (Hypervisor)

![Alt text](/cloud_uptime_sla.png?raw=true "")

* Perform API login to cloud components
* Update any downtime to SLA DB  
* Record consolidate downtime on monthly report
