import React from 'react';
import { connect } from 'react-redux';
import { Link } from 'react-router';

import * as AuthActions from '../actions/auth_actions.jsx';

const AppLayout = React.createClass({
  render() {
    let onClickLogout = e => { this.props.dispatch(AuthActions.logout()); };
    let authNodes = this.props.isAuthenticated ?
      <ul className='nav navbar-nav navbar-right'><li><Link to='/account'><span className='glyphicon glyphicon-user'></span> {this.props.username}</Link></li><li><a onClick={onClickLogout}><span className='glyphicon glyphicon-log-out'></span> Logout</a></li></ul> :
      <ul className='nav navbar-nav navbar-right'><li><Link to='/login'><span className='glyphicon glyphicon-log-in'></span> Login</Link></li></ul>
    return (
      <div>
        <nav className='navbar navbar-inverse navbar-fixed-top'>
          <div className='container-fluid'>
            <div className='navbar-header'>
              <button type='button' className='navbar-toggle collapsed' data-toggle='collapse' data-target='#navbar' aria-expanded='false' aria-controls='navbar'>
                <span className='sr-only'>Toggle navigation</span>
                <span className='icon-bar'></span>
                <span className='icon-bar'></span>
                <span className='icon-bar'></span>
              </button>
              <a className='navbar-brand' href='#'>SGD Admin</a>
            </div>
            <div id='navbar' className='navbar-collapse collapse'>
              {authNodes}
            </div>
          </div>
        </nav>

        <div className='container-fluid'>
          <div className='row application-row'>
            <div className='col-sm-12 main' style={{ marginTop: '3rem' }}>
              {this.props.children}
            </div>
          </div>
        </div>
      </div>
    );
  }
});

function mapStateToProps(_state) {
  let state = _state.auth;
  return {
    isAuthenticated: state.isAuthenticated,
    isAuthenticating: state.isAuthenticating,
    username: state.username
  };
};

module.exports = connect(mapStateToProps)(AppLayout);
