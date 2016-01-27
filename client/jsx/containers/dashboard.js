import React from 'react';
import { Link } from 'react-router';

const Dashboard = React.createClass({
  render() {
    return (
      <div>
        <div className='col-sm-1'>
          <div className='btn-group-vertical' role='group'>
            <Link to='/dashboard' className='btn btn-default'><span className='glyphicon glyphicon-home' /> Home</Link>
            <Link to='/dashboard/files' className='btn btn-default'><span className='glyphicon glyphicon-floppy-disk' /> Files</Link>
          </div>
        </div>
        <div className='col-sm-11'>
          {this.props.children}
        </div>
      </div>
    );
  }
});

module.exports = Dashboard;
