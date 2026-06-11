from __future__ import annotations


RAW_SKILL_CATALOG: dict[str, list[str]] = {
    "Linux": [
        "Linux", "Ubuntu", "Debian", "CentOS", "RHEL", "Red Hat", "Rocky Linux", "AlmaLinux", "Fedora",
        "SUSE", "openSUSE", "Oracle Linux", "Arch Linux", "Gentoo", "FreeBSD", "Unix", "systemd", "journald",
        "cron", "crontab", "bash", "shell", "sh", "zsh", "fish", "awk", "sed", "grep", "find", "xargs",
        "rsync", "scp", "ssh", "sshd", "sudo", "iptables", "nftables", "firewalld", "ufw", "SELinux",
        "AppArmor", "LVM", "mdadm", "RAID", "NFS", "Samba", "CIFS", "iSCSI", "GlusterFS", "Ceph",
        "Btrfs", "XFS", "ext4", "ZFS", "logrotate", "rsyslog", "syslog-ng", "OpenSSH", "Fail2ban",
        "Postfix", "Dovecot", "Exim", "Bind", "Unbound", "Keepalived", "HAProxy", "Pacemaker", "Corosync",
        "Anacron", "NetworkManager", "Netplan", "YUM", "DNF", "APT", "RPM", "DEB", "Kickstart", "Preseed",
    ],
    "Windows": [
        "Windows", "Windows Server", "Windows 10", "Windows 11", "Active Directory", "AD DS", "LDAP",
        "Group Policy", "GPO", "DNS Server", "DHCP Server", "IIS", "PowerShell", "PowerShell Core",
        "WinRM", "WMI", "RDP", "Remote Desktop", "Hyper-V", "Failover Cluster", "WSUS", "SCCM",
        "Microsoft Configuration Manager", "Intune", "Microsoft 365", "Office 365", "Exchange Server",
        "Exchange Online", "SharePoint", "OneDrive", "Azure AD", "Entra ID", "DFS", "File Server",
        "Print Server", "BitLocker", "Defender", "Windows Defender", "NTFS", "ReFS", "Kerberos", "NTLM",
        "RDS", "Terminal Server", "Windows Admin Center", "Event Viewer", "Task Scheduler", "MSSQL Server",
        "SQL Server", "ADFS", "PKI", "Certificate Services", "CA", "RemoteApp", "FSLogix", "MDT", "WDS",
    ],
    "Networking": [
        "TCP/IP", "TCP", "UDP", "IP", "IPv4", "IPv6", "DNS", "DHCP", "VPN", "IPsec", "OpenVPN",
        "WireGuard", "L2TP", "PPTP", "GRE", "VLAN", "VXLAN", "LAN", "WAN", "WLAN", "Wi-Fi", "802.1Q",
        "802.1X", "NAT", "PAT", "Routing", "Switching", "BGP", "OSPF", "EIGRP", "RIP", "MPLS", "QoS",
        "ACL", "Firewall", "Proxy", "Reverse Proxy", "Load Balancing", "Cisco", "Mikrotik", "Juniper",
        "Huawei", "HPE Aruba", "Fortinet", "FortiGate", "Palo Alto", "Check Point", "pfSense", "OPNsense",
        "Ubiquiti", "UniFi", "SNMP", "NetFlow", "sFlow", "ICMP", "ARP", "NTP", "SMTP", "IMAP", "POP3",
        "HTTP", "HTTPS", "TLS", "SSL", "REST", "SOAP", "WebSocket", "MQTT", "Radius", "TACACS",
    ],
    "Virtualization": [
        "VMware", "VMware vSphere", "VMware ESXi", "vCenter", "vSAN", "NSX", "VMware Workstation",
        "Hyper-V", "Proxmox", "KVM", "QEMU", "libvirt", "VirtualBox", "Xen", "Citrix Hypervisor",
        "Nutanix", "AHV", "OpenStack", "LXC", "LXD", "Docker", "containerd", "Podman", "CRI-O",
        "Kubernetes", "K8s", "OpenShift", "Rancher", "Helm", "Ingress", "Istio", "Linkerd", "Longhorn",
        "Portainer", "Harbor", "Minikube", "kind", "kubeadm", "Kubectl", "Docker Compose", "Docker Swarm",
        "Vagrant", "Packer", "Cloud-init", "Terraform", "Ansible", "Puppet", "Chef", "SaltStack",
    ],
    "DevOps": [
        "Git", "GitLab", "GitHub", "Bitbucket", "Jenkins", "TeamCity", "Bamboo", "GitLab CI", "GitHub Actions",
        "Azure DevOps", "CI/CD", "CI", "CD", "Argo CD", "FluxCD", "Tekton", "Drone CI", "CircleCI",
        "Travis CI", "Ansible", "Terraform", "Terragrunt", "Pulumi", "Packer", "Vault", "Consul", "Nomad",
        "Nexus", "Artifactory", "SonarQube", "Sentry", "ELK", "Elastic Stack", "Logstash", "Kibana",
        "Fluentd", "Fluent Bit", "Graylog", "Make", "CMake", "Maven", "Gradle", "npm", "Yarn", "pnpm",
        "pip", "Poetry", "pipenv", "Dockerfile", "Compose", "registry", "container registry", "Blue Green",
        "Canary", "Rolling update", "IaC", "Infrastructure as Code", "DevSecOps", "GitOps",
    ],
    "Monitoring": [
        "Zabbix", "Grafana", "Prometheus", "Alertmanager", "VictoriaMetrics", "InfluxDB", "Telegraf",
        "Nagios", "Icinga", "Centreon", "PRTG", "Cacti", "Netdata", "Datadog", "New Relic", "Dynatrace",
        "Splunk", "ELK", "OpenSearch", "Kibana", "Loki", "Promtail", "Jaeger", "Zipkin", "OpenTelemetry",
        "Sentry", "Uptime Kuma", "Blackbox Exporter", "Node Exporter", "cAdvisor", "Grafana Agent",
        "CloudWatch", "Azure Monitor", "Google Cloud Monitoring", "SNMP", "Syslog", "log monitoring",
        "APM", "tracing", "metrics", "dashboards", "alerts", "SLA", "SLO", "SLI",
    ],
    "Databases": [
        "PostgreSQL", "MySQL", "MariaDB", "MongoDB", "Redis", "ClickHouse", "Elasticsearch", "OpenSearch",
        "Oracle", "Oracle Database", "MS SQL", "SQL Server", "SQLite", "Cassandra", "ScyllaDB", "DynamoDB",
        "CouchDB", "Neo4j", "InfluxDB", "TimescaleDB", "Greenplum", "Vertica", "Hadoop", "HDFS", "Hive",
        "Spark", "Kafka", "RabbitMQ", "ActiveMQ", "NATS", "etcd", "Consul KV", "MinIO", "S3", "SQL",
        "NoSQL", "PL/SQL", "T-SQL", "replication", "backup", "restore", "pgAdmin", "phpMyAdmin", "Liquibase",
        "Flyway", "SQLAlchemy", "DBeaver", "DataGrip",
    ],
    "Cloud": [
        "AWS", "Amazon Web Services", "Azure", "Microsoft Azure", "GCP", "Google Cloud", "Yandex Cloud",
        "VK Cloud", "Selectel", "OpenStack", "Cloudflare", "DigitalOcean", "Hetzner", "Linode", "S3",
        "EC2", "ECS", "EKS", "Lambda", "RDS", "Route 53", "CloudFront", "IAM", "VPC", "ELB", "ALB", "NLB",
        "CloudWatch", "CloudTrail", "Azure VM", "AKS", "Azure Functions", "Blob Storage", "Azure SQL",
        "Azure Monitor", "GKE", "Cloud Run", "Cloud Functions", "Compute Engine", "Cloud SQL", "BigQuery",
        "Terraform Cloud", "CDN", "object storage", "serverless", "managed Kubernetes",
    ],
    "Security": [
        "Information Security", "ИБ", "SOC", "SIEM", "DLP", "EDR", "XDR", "IDS", "IPS", "WAF", "Firewall",
        "Antivirus", "Kaspersky", "Dr.Web", "Defender", "CrowdStrike", "SentinelOne", "Nessus", "OpenVAS",
        "Qualys", "Burp Suite", "OWASP", "SAST", "DAST", "Vulnerability Management", "Pentest", "Hardening",
        "CIS Benchmarks", "ISO 27001", "PCI DSS", "GDPR", "Zero Trust", "MFA", "2FA", "SSO", "OAuth",
        "OpenID Connect", "SAML", "Kerberos", "PKI", "TLS", "SSL", "certificates", "Vault", "Secrets",
        "HashiCorp Vault", "Keycloak", "RBAC", "ABAC", "audit", "incident response", "forensics",
    ],
    "Programming": [
        "Python", "Bash", "PowerShell", "Go", "Golang", "Java", "JavaScript", "TypeScript", "Node.js",
        "C#", "C++", "C", "PHP", "Ruby", "Perl", "Rust", "Kotlin", "Swift", "Scala", "Groovy", "Lua",
        "Dart", "R", "MATLAB", "HTML", "CSS", "Sass", "React", "Vue", "Angular", "Django", "Flask",
        "FastAPI", "Spring", "ASP.NET", ".NET", "Express", "NestJS", "REST API", "GraphQL", "gRPC",
        "JSON", "XML", "YAML", "TOML", "regex", "unit tests", "pytest", "unittest", "JMeter", "Postman",
        "Swagger", "OpenAPI", "Selenium", "Playwright",
    ],
}

SOFT_SKILLS = [
    "коммуникабельность", "ответственность", "обучаемость", "внимательность", "стрессоустойчивость",
    "командная работа", "аналитическое мышление", "самостоятельность", "инициативность", "тайм-менеджмент",
]

CERTIFICATES = [
    "CCNA", "CCNP", "CCIE", "MTCNA", "MTCRE", "RHCSA", "RHCE", "LPIC", "ITIL", "AWS Certified",
    "Azure Administrator", "CKA", "CKAD", "Security+", "Network+", "CompTIA", "PMP",
]


def _expanded_catalog() -> dict[str, list[str]]:
    catalog: dict[str, list[str]] = {}
    for category, skills in RAW_SKILL_CATALOG.items():
        expanded = list(skills)
        if category in {"Linux", "Windows", "Databases"}:
            for skill in skills[:45]:
                expanded.extend([f"{skill} administration", f"администрирование {skill}"])
        if category in {"DevOps", "Virtualization", "Cloud"}:
            for skill in skills[:45]:
                expanded.extend([f"{skill} automation", f"{skill} deployment"])
        if category in {"Networking", "Monitoring", "Security"}:
            for skill in skills[:45]:
                expanded.extend([f"{skill} monitoring", f"{skill} troubleshooting"])
        catalog[category] = list(dict.fromkeys(expanded))
    return catalog


SKILL_CATALOG = _expanded_catalog()
TECHNICAL_SKILLS = sorted({skill for skills in SKILL_CATALOG.values() for skill in skills})
