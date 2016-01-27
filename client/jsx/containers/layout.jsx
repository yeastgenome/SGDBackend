import React from 'react';
import { connect } from 'react-redux';

const AppLayout = React.createClass({
  render() {
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
              <ul className='nav navbar-nav navbar-right'>
                <li><a href='#'><span className='glyphicon glyphicon-log-out'></span> Logout</a></li>
              </ul>
            </div>
          </div>
        </nav>

        <div className='container-fluid'>
          <div className='row application-row'>
            <div className='col-sm-12 main'>
              <h1>Hola Mundo</h1>
            </div>
          </div>
        </div>
      </div>
    );
  }
});

function mapStateToProps(_state) {
  return {
  };
}

module.exports = connect(mapStateToProps)(AppLayout);
