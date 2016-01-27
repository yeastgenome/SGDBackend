import React, { Component } from 'react';
import { Router, Route } from 'react-router';
import { syncReduxAndRouter } from 'redux-simple-router';
import { Provider } from 'react-redux';
import { createHashHistory, useQueries } from 'history'

// import store config and routes
const ConfigureStore = require('./store/configure_store.jsx');
const Routes = require('./routes.jsx');

const ReduxApplication = React.createClass({
  render() {
    // configure store, with history in redux state
    let store = ConfigureStore(true);

    let history = useQueries(createHashHistory)();
    syncReduxAndRouter(history, store);

    return (
      <Provider store={store}>
        <Router history={history}>
          {Routes}
        </Router>
      </Provider>
    );
  }
});

module.exports = ReduxApplication;
