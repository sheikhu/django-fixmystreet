Vagrant::Config.run do |config|
  config.vm.box = "cirb-6-64"
  #config.vm.boot_mode = :gui
  config.vm.host_name = "fixmystreet_jenkins.ad.cirb.lan"
  config.ssh.max_tries = 333
  config.vm.forward_port 22, 2222
  config.vm.forward_port 80, 8080
  config.vm.forward_port 5432, 5433
  config.vm.forward_port 6180, 6180
  config.vm.provision :puppet do |puppet|
    puppet.module_path = "/etc/puppet/modules"
    puppet.manifests_path = "/etc/puppet/manifests"
    puppet.manifest_file  = "site-dev.pp"
    puppet.options  = ["--environment dev"] # "--debug"
    puppet.pp_path = "/vagrant"
  end
  config.vm.share_folder "hieradata", "/vagrant/hieradata", "/etc/puppet/hieradata"
end
