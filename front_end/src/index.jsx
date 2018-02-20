import React from 'react';
import ReactDOM from 'react-dom';

import AppRoutes from './routing';
import BasicExample from './components/routingExample'
import ParamsExample from './components/urlParameterExample'

import './styles/app.scss';
ReactDOM.render(
    <ParamsExample/>,
    document.getElementById('root')
);
