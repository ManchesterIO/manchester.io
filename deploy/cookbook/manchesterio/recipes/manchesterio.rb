include_recipe "manchesterio::system"

unless node['manchesterio']['vagrant']

  remote_directory "#{node['manchesterio']['root']}/api" do
    source "api"
  end

  remote_directory "#{node['manchesterio']['root']}/static" do
    source "static"
  end

  cookbook_file "#{node['manchesterio']['root']}/package.json" do
    source "package.json"
  end

  cookbook_file "#{node['manchesterio']['root']}/yarn.lock" do
    source "yarn.lock"
    user node['manchesterio']['user']
  end

  cookbook_file "#{node['manchesterio']['root']}/build/sri.json" do
    source "sri.json"
  end

  systemd_unit 'manchesterio.service' do
    content <<-EOU.gsub(/^\s+/, '')
      [Unit]
      Description=Manchester.IO

      [Service]
      Type=simple
      ExecStart=/usr/bin/node api/server.js
      Restart=on-failure
      User=#{node['manchesterio']['user']}
      Group=#{node['manchesterio']['user']}
      WorkingDirectory=#{node['manchesterio']['root']}
      Environment=NODE_ENV=#{node['manchesterio']['debug'] ? 'development' : 'production'}
    
      [Install]
      WantedBy=multi-user.service
    EOU

    action [:create, :enable, :start]
  end

end

execute 'yarn install' do
  command "/usr/bin/yarn"
  cwd node['manchesterio']['root']
  user node['manchesterio']['user']
  environment ({
      'HOME' => node['manchesterio']['root'],
      'NODE_ENV' => node['manchesterio']['debug'] ? 'development' : 'production',
  })
end
