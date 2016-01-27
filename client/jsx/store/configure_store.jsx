import { createStore, compose, applyMiddleware, combineReducers } from 'redux';
import thunk from 'redux-thunk';
import { routeReducer } from 'redux-simple-router';

// custom reducers
const authReducer = require('../reducers/auth_reducer.jsx');

// add history to reducer and thunk to dispatch functions as actions
const ConfigureStore = (useRouterReducer, initialState) => {
  let reducerObj = {
    auth: authReducer,
    routing: routeReducer,
  };
  const reducer = combineReducers(reducerObj);

  let store = compose(
    applyMiddleware(thunk)
  )(createStore)(reducer, initialState);
  return store;
};

module.exports = ConfigureStore;
