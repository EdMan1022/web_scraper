import React from "react";
import { BrowserRouter as Router, Route, Link } from "react-router-dom";

import {Home, Car, About} from "./components/index";
import Game from "./components/HelloWorld";

const AppRoutes = () => (
    <Router>
        <div>
            <Route exact path="/" component={Home}/>
            <Route path="/car" component={Car}/>
            <Route path="/about" component={About}/>
            <Route path="/game" component={Game}/>
        </div>
    </Router>
);

export default AppRoutes
