remote_directory "/srv/manchester.io/app" do
  source "app"
end

remote_directory "/srv/manchester.io/static" do
  source "static"
end

%w(cache logs meta sessions views).each do | subdir |
  directory "/srv/manchester.io/app/app/storage/#{subdir}" do
    owner "www-data"
  end
end