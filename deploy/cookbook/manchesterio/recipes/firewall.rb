include_recipe "firewall"

firewall 'ufw' do
  action :install
end

firewall_rule "ssh" do
  port 22
  command :allow
end

firewall_rule "http" do
  port 80
  protocol :tcp
  command :allow
end

firewall_rule "https" do
  port 443
  protocol :tcp
  command :allow
end
