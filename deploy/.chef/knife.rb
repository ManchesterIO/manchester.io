cookbook_path %w(cookbooks site-cookbooks)
node_path 'nodes'
role_path 'roles'
data_bag_path 'data_bags'
encrypted_data_bag_secret "encrypted_data_bag_secret"

knife[:berkshelf_path] = 'cookbooks'
knife[:ssh_user] = 'deploy'
knife[:use_sudo] = true