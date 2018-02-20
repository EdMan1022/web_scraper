import React, { Component } from 'react';
import {render} from 'react-dom';

export class Home extends Component {
    render(){
        return (<h1>Home Page</h1>);
    }
}

// More components
export class Car extends Component {
    render(){
        return (<h1>Cars page</h1>);
    }
}

export class About extends Component {
    render(){
        return (<h1>About page</h1>);
    }
}

export default Home;
export default Car;
export default About;
