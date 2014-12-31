include_recipe "graphite::carbon"

graphite_storage_schema "default_1min_for_1day" do
  config ({
      pattern: ".*",
      retentions: "1m:1y"
  })
end

graphite_carbon_cache "default" do
  config ({
      enable_logrotation: true,
      user: "graphite",
      max_cache_size: "inf",
      max_updates_per_second: 500,
      max_creates_per_minute: 50,
      line_receiver_interface: "0.0.0.0",
      line_receiver_port: 2003,
      udp_receiver_port: 2003,
      pickle_receiver_port: 2004,
      enable_udp_listener: true,
      cache_query_port: "7002",
      cache_write_strategy: "sorted",
      use_flow_control: true,
      log_updates: false,
      log_cache_hits: false,
      whisper_autoflush: false,
      local_data_dir: "#{node.graphite.storage_dir}/whisper/"
  })
end

graphite_service "cache"

execute "python manage.py syncdb --noinput" do
  user node['graphite']['user']
  group node['graphite']['group']
  cwd "#{node.graphite.base_dir}/webapp/graphite"
end
