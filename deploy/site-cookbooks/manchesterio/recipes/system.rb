user node.manchesterio.user do
  home node.manchesterio.root
end

['', 'bin', 'data'].each do | extension |
  directory "#{node.manchesterio.root}/#{extension}" do
    owner node.manchesterio.user
    group node.manchesterio.user
  end
end
