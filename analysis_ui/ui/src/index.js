import React from 'react';
import ReactDOM from 'react-dom';
import Image from 'react-image';

// From: https://github.com/react-component/slider
import Slider, { Range } from 'rc-slider';

import './index.css';
import 'rc-slider/assets/index.css';

import imagey from './test/images';

function log(value) {
  console.log(value); //eslint-disable-line
}

function pad(num, size) {
    var s = num+"";
    while (s.length < size) s = "0" + s;
    return s;
}

function Square(props) {
    return (
          <button
            className="square"
            onClick={ ()=> props.onClick() }
            >
                {props.value}
          </button>

    );
}

class Results extends React.Component {

    constructor(props) {
        super(props);
        this.state = {
            value: 0,
            valueStr: '',
        };
    }
    
    renderSquare(i) {
    }

    handleClick(i) {
    }

    onSliderChange = (value) => {
        log(value);
        this.setState( {
            value: value,
            valueStr: pad(value,3),
        })
    };

    render() {

        const createSliderWithTooltip = Slider.createSliderWithTooltip;
        const TRange = createSliderWithTooltip(Slider.Range);

        return (
                <div>

            here: {this.state.valueStr }

                <div className="intphys_img">
                <img src={ imagey.image1 } />
                &nbsp;
                <img src={ imagey.image2 } />
                &nbsp;
                <img src={ imagey.image3 } />
                &nbsp;
                <img src={ imagey.image4 } />
                </div>
                <div className="slider">
                <Slider
            value={this.state.value}
            onChange={this.onSliderChange} />
                </div>
                
            </div>
        );
    }
}


class EvalUI extends React.Component {

    // Assume that we are called with a URL like:
    // http://localhost:3000/app/perf=Bob&subm=ABC&block=O3&test=123
    // Parse that and put it into the state
    constructor(props) {
        super(props);

        this.state = {
            perf: 'TA1-Test',
            subm: 'ABC',
            block: 'O3',
            test: '123',
        };
    }
    
    render() {

        return (
                <div className="layout">

                <div className="header">
                <div className="title">Performer: { this.state.perf }</div>
                <div className="title">Submission: { this.state.subm }</div>
                <div className="title">Block: { this.state.block }</div>
                <div className="title">Test: { this.state.test }</div>
                </div>
                
                <div className="layout-board">
                   <Results value={this.state}/>
                </div>

            </div>
        );
    }
}

// ========================================

ReactDOM.render(
        <EvalUI />,
        document.getElementById('root')
);
