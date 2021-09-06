FROM grafana/grafana:7.5.5

ADD datasources/ /etc/grafana/provisioning/datasources/
ADD dashboards/ /etc/grafana/provisioning/dashboards/

RUN mkdir -p /var/lib/grafana/dashboards

COPY fed_dashboard.json /var/lib/grafana/dashboards
COPY demonstration.json /var/lib/grafana/dashboards
