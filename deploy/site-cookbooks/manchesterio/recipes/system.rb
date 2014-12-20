user node.manchesterio.user do
  home node.manchesterio.root
end

directory node.manchesterio.root do
  owner node.manchesterio.user
  group node.manchesterio.user
end

directory "#{node.manchesterio.root}/bin" do
  owner node.manchesterio.user
  group node.manchesterio.user
end
