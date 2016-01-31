import React from 'react';
import Radium from 'radium';
import { connect } from 'react-redux';
import { Link } from 'react-router';
import * as AuthActions from '../actions/auth_actions';

const AppLayout = React.createClass({
  render() {
    let onClickLogout = e => {
      e.preventDefault();
      this.props.dispatch(AuthActions.logoutAndRedirect());
    };
    // init auth nodes, either login or logout links
    let authNodes = this.props.isAuthenticated ?
      <ul style={styles.menu} className='menu'><li><Link style={styles.navLink} to='/account'><i className='fa fa-user'></i> {this.props.username}</Link></li><li><a style={styles.navLink} onClick={onClickLogout} href='#'><i className='fa fa-sign-out'></i> Logout</a></li></ul> :
      <ul style={styles.menu} className='menu'><li><Link style={styles.navLink} to='/login'><i className='fa fa-sign-in'></i> Login</Link></li></ul>;
    return (
      <div>
        <nav className='top-bar' style={styles.messageZone}>
          <p>Have a look at our <a>cookies policy</a>. and <a>privacy policy.</a></p>
        </nav>
        <nav className='top-bar' style={styles.navWrapper}>
          <div className='top-bar-left'>
            <ul className='menu' style={styles.menu}>
              <li>
                <Link to='dashboard' style={styles.navLink}>
                  <p>SGD Admin</p>
                </Link>
              </li>
            </ul>
          </div>
         <div className='top-bar-right'>
          {authNodes}
        </div>
        </nav>
        <div className='row full-width wrapper'>
          <div className='large-12 columns'>
            {this.props.children}
          </div>
        </div>
      </div>
    );
  }
});

const purple = '#663882';
const red = '#C22D38';
const messageColor = '#CCC';
var styles = {
  messageZone: {
    background: 'black',
    color: messageColor
  },
  menu: {
    background: 'none',
    fontSize: '18px'
  },
  navWrapper: {
    background: purple
  },
  navLink: {
    color: 'white',
    background: 'none'
  },
  indexLink: {
    color: 'black'
  }
};

function mapStateToProps(_state) {
  let state = _state.auth;
  return {
    isAuthenticated: state.isAuthenticated,
    isAuthenticating: state.isAuthenticating,
    username: state.username
  };
};

module.exports = Radium(connect(mapStateToProps)(AppLayout));
