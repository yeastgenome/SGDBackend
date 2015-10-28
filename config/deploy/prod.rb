set :stage, :prod

set :user, ask('Username', nil)
set :tmp_dir, "/home/#{fetch(:user)}/tmp"

set :branch, ENV['BRANCH'] || $1 if `git branch` =~ /\* (\S+)\s/m

server ENV['SERVER_1'], user: fetch(:user), port: 22, roles: %w{app}
server ENV['SERVER_2'], user: fetch(:user), port: 22, roles: %w{app}

namespace :deploy do
  after :finishing, :build
  after :finishing, :write_config
  after :finishing, :restart
end
