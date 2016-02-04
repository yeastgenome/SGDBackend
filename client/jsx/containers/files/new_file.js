import React from 'react';
import Dropzone from 'react-dropzone';
import { connect } from 'react-redux';
import { Link } from 'react-router';

const FilesIndex = React.createClass({
  render() {
    return (
      <div>
        <h1>Dataset Upload</h1>
        <div className='panel'>
          <p>File</p>
          <Dropzone onDrop={this._onDrop}>
            <p>Drop file here or click to select.</p>
          </Dropzone>
          <div className='button-group'>
           <Link to='/dashboard/files' className='button secondary'>Cancel</Link>
           <a className='button disabled'><i className='fa fa-upload'/> Upload</a>
          </div>
        </div>
      </div>
    );
  },

  _onDrop (files) {
      console.log('Received files: ', files);
    },
});

function mapStateToProps(_state) {
  return {
  };
}

module.exports = connect(mapStateToProps)(FilesIndex);
