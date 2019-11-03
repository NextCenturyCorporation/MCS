import React from 'react';
import ReactDOM from 'react-dom';
import Image from 'react-image';
// From: https://github.com/react-component/slider
import Slider, { Range } from 'rc-slider';

// Images from Test
import { imagey_1, imagey_2, imagey_3, imagey_4 } from './test/images';

// CSS Stuff 
import './index.css';
import 'rc-slider/assets/index.css';

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
        this.setState( {
            value: value,
            valueStr: pad(value,3),
        })
    };

    render() {

        const v = this.state.value;

        return (
                <div>

                <div className="intphys_img">
                <img src={ imagey_1[v] } />
                &nbsp;
                <img src={ imagey_2[v] } />
                &nbsp;
                <img src={ imagey_3[v] } />
                &nbsp;
                <img src={ imagey_4[v] } />
                &nbsp;
                </div>
                            Frame: {v}
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
