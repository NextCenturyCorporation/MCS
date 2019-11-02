import React from 'react';
import ReactDOM from 'react-dom';

// From: https://github.com/react-component/slider
import Slider, { TRange } from 'rc-slider';

import './index.css';
import 'rc-slider/assets/index.css';


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

class Board extends React.Component {

    constructor(props) {
        super(props);
        this.state = {
            squares: Array(9).fill(null),
            xIsNext: true,
        };
    }
    
    renderSquare(i) {
        return <Square
        value={this.state.squares[i]}
        onClick = { () => this.handleClick(i) }
        />;
    }

    handleClick(i) {
        const squares = this.state.squares.slice();

        if (calculateWinner(squares) || squares[i]) {
            return;
        }
        
        squares[i] = this.state.xIsNext ? 'X' : 'O';
        this.setState( {
            squares: squares,
            xIsNext: !this.state.xIsNext
        });
    }

    render() {

        const winner = calculateWinner(this.state.squares);
        let status;
        if (winner) {
            status = 'Winner: ' + winner;
        } else {
            status = 'Next player: ' + (this.state.xIsNext ? 'X' : 'O');
        }

        const createSliderWithTooltip = Slider.createSliderWithTooltip;
        const TRange = createSliderWithTooltip(Slider);

        return (
                <div>

                <div className="status">{status}</div>

                <div className="board-row">
                {this.renderSquare(0)}
            {this.renderSquare(1)}
            {this.renderSquare(2)}
            </div>

                <div className="board-row">
                {this.renderSquare(3)}
            {this.renderSquare(4)}
            {this.renderSquare(5)}
            </div>

                <div className="board-row">
                {this.renderSquare(6)}
            {this.renderSquare(7)}
            {this.renderSquare(8)}
            
            </div>

                <div className="slider">
                <TRange />
                </div>

            </div>
        );
    }
}

function calculateWinner(squares) {
    const lines = [
        [0, 1, 2],
        [3, 4, 5],
        [6, 7, 8],
        [0, 3, 6],
        [1, 4, 7],
        [2, 5, 8],
        [0, 4, 8],
        [2, 4, 6],
    ];
    for (let i = 0; i < lines.length; i++) {
        const [a, b, c] = lines[i];
        if (squares[a] && squares[a] === squares[b] && squares[a] === squares[c]) {
            return squares[a];
        }
    }
    return null;
}


class EvalUI extends React.Component {

    // Assume that we are called with a URL like:
    // http://localhost:3000/app/perf=Bob&subm=ABC&block=O3&test=123
    constructor(props) {
        super(props);
        this.state = {
            perf: 'bob',
            subm: 'ABC',
            block: 'O3',
            test: '123',
        };
    }
    
    
    render() {
        return (
            <div className="game">
                
                <div className="game-board">
                   <Board />
                </div>

                <div className="game-info">
                   <div>{/* status */}</div>
                   <ol>{/* TODO */}</ol>
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
