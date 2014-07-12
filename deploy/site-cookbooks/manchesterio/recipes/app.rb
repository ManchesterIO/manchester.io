remote_directory "/srv/manchester.io/app" do
  source "app"
end

remote_directory "/srv/manchester.io/static" do
  source "static"
end

directory "/srv/manchester.io/app/views/template_cache" do
  owner "www-data"
end
