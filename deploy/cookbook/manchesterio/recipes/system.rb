user node['manchesterio']['user'] do
  home node['manchesterio']['root']
end

['', 'build'].each do | subdir |
  directory "#{node['manchesterio']['root']}/#{subdir}" do
    owner node['manchesterio']['user']
    group node['manchesterio']['user']
  end
end

apt_update 'all platforms' do
  frequency 86400
  action :periodic
end

apt_repository "nodesource" do
  uri "https://deb.nodesource.com/node_6.x"
  arch 'amd64'
  distribution node["lsb"]["codename"]
  components ["main"]
  key "https://deb.nodesource.com/gpgkey/nodesource.gpg.key"
end

package 'nodejs'

apt_repository 'yarn' do
  uri 'https://dl.yarnpkg.com/debian/'
  distribution 'stable'
  components %w(main)
  key 'https://dl.yarnpkg.com/debian/pubkey.gpg'
end

package 'yarn'
