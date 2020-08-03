import React from 'react';
import queryString from 'query-string';
import Results from './results';
import Scenes from './scenes';
import EvalHeader from './header';
import CommentsComponent from './comments'

// CSS Stuff 
import '../../css/app.css';
import 'rc-slider/assets/index.css';
import 'bootstrap/dist/css/bootstrap.min.css';
import 'material-design-icons/iconfont/material-icons.css'

export class App extends React.Component {

    // Assume that we are called with a URL like:
    // http://localhost:3000/app/?perf=TA1_group_test&subm=submission_0&block=O1&test=0001

    constructor(props) {
        super(props);

        this.state = queryString.parse(window.location.search);
        this.state.showComments = (process.env.REACT_APP_COMMENTS_ON.toLowerCase() === 'true' || process.env.REACT_APP_COMMENTS_ON === '1');
    }

    render() {
        return (
            <div>
                <div className="layout">

                    <EvalHeader state={this.state}/>

                    <div className="layout-board">
                        { (this.state.perf !== undefined && this.state.perf !== null) && <Results value={this.state}/>}
                        { (this.state.test_type !== undefined && this.state.test_type !== null) && <Scenes value={this.state}/> }
                        { this.state.showComments &&  <CommentsComponent state={this.state}/> }
                    </div>
                </div>
            </div>
        );
    }
}