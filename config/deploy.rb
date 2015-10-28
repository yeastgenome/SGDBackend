lock '3.4.0'

set :application, 'SGDBackend'
set :repo_url, 'git://github.com/yeastgenome/SGDBackend.git'

set :deploy_to, '/data/www/' + fetch(:application) + '_app'

set :format, :pretty
set :log_level, :debug

set :default_stage, "dev"

set :keep_releases, 5

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
end
