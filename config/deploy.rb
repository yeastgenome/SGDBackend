lock '3.4.0'

set :application, 'SGDBackend'

set :repo_url, 'git://github.com/yeastgenome/SGDBackend.git'
set :branch, ENV['BRANCH'] || $1 if `git branch` =~ /\* (\S+)\s/m
set :deploy_to, '/data/www/' + fetch(:application) + '_app'
set :tmp_dir, "/home/#{fetch(:user)}/tmp"

set :user, ask('Username', nil)

set :default_stage, "dev"

set :keep_releases, 5
set :format, :pretty
set :log_level, :debug

namespace :deploy do
  desc 'Build application'
  task :build do
    on roles(:app), in: :sequence do
      execute "export ORACLE_HOME=/data/tools/oracle_instant_client/instantclient_11_2/ && export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$ORACLE_HOME && cd #{release_path} && make build-deploy"
    end
  end

  desc 'Restart Apache'
  task :restart do
    on roles(:app), in: :sequence do
      execute "sudo /usr/sbin/apachectl graceful"
    end
  end

  desc 'Write config file'
  task :write_config do
    on roles(:app), in: :sequence do
      config_file_content = ""
      ["DBTYPE", "DBNAME", "NEX_DBHOST", "NEX_SCHEMA", "NEX_DBUSER", "NEX_DBPASS", "PERF_DBHOST", "PERF_SCHEMA", "PERF_DBUSER", "PERF_DBPASS"].each do |key|
        config_file_content += "#{key} = '#{ENV[key]}'\n"
      end
      config_file_content += "elasticsearch_address = '#{ENV['ELASTICSEARCH_ADDRESS']}'\n"
      config_file_content += "sgdbackend_log_directory = None\n"
      config_file_content += "perfbackend_log_directory = None\n"

      execute "echo \"#{config_file_content}\" >> #{current_path}/src/sgd/backend/config.py && rm #{current_path}/src/sgd/backend/config.py.template"
    end
  end

  desc 'Recreates symbolic link if broken'
  task :verify_symlink do
    on roles(:app), in: :sequence do
      execute "cd #{current_path}/../../ && if [ -h SGDBackend ] && [ $(readlink SGDBackend_app/current) != $(readlink SGDBackend) ]; then echo \"Restoring symlink...\" && rm SGDBackend && ln -s SGDBackend_app/current SGDBackend; fi"
    end
  end

  after :finishing, :write_config
  after :finishing, :build
  after :finishing, :verify_symlink
  after :finishing, :restart
end
