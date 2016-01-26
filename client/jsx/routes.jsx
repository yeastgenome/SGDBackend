import React from 'react';
import { Route } from 'react-router';

// import handler containers
const Layout = require('./containers/layout.jsx');

const ExampleContainer = require('./containers/example_container.jsx');
const NotFound = require('./containers/not_found.jsx');

module.exports = (
  <Route path='/' component={Layout}>
    <Route path='example' component={ExampleContainer} />
    <Route path='*' component={NotFound}/>
  </Route>
);
