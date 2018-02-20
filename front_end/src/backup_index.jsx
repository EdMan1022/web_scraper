import React from 'react';
import ReactDOM from 'react-dom';
import {Router, Route} from 'react-router';

import Game from './components/HelloWorld';
import {Home, Car, About} from './components/index';


import './styles/app.scss';
ReactDOM.render(
    <About/>,
    document.getElementById('root')
);
