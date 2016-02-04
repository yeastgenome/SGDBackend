import React from 'react';
import { connect } from 'react-redux';
import { Link } from 'react-router';

const FilesIndex = React.createClass({
  render() {
    return (
      <div>
        <h1>Datasets</h1>
        <Link to='/dashboard/files/new'className='button'><i className='fa fa-plus'/> New Dataset</Link>
      </div>
    );
  }
});

function mapStateToProps(_state) {
  return {
  };
}

module.exports = connect(mapStateToProps)(FilesIndex);
