import React from 'react';
import { connect } from 'react-redux';

const Login = React.createClass({
  render() {
      // TEMP
    let loginAction = {
      type: 'AUTHENTICATE_USER'
    };
    let _onClick = e => {
      e.preventDefault()
      this.props.dispatch(loginAction);
    };

    return (
      <div>
        <h1>Login</h1>
        <a className='btn btn-default' href='#' onClick={_onClick}>Login</a>
      </div>
    );
  }
});

function mapStateToProps(_state) {
  return {
  };
}

module.exports = connect(mapStateToProps)(Login);
