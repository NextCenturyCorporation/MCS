import React from 'react';
import queryString from 'query-string';
import Results from './results';
import EvalHeader from './header';
import CommentsComponent from './comments'

// CSS Stuff 
import '../../css/app.css';
import 'rc-slider/assets/index.css';

export class App extends React.Component {

    // Assume that we are called with a URL like:
    // http://localhost:3000/app/?perf=TA1_group_test&subm=submission_0&block=O1&test=0001

    constructor(props) {
        super(props);

        this.state = queryString.parse(window.location.search);
    }

    render() {
        return (
            <div>
                <div className="layout">

                    <EvalHeader state={this.state}/>
                    
                    <div className="layout-board">
                        <Results value={this.state}/>
                        <CommentsComponent state={this.state}/>
                    </div>
                </div>
            </div>
        );
    }
}