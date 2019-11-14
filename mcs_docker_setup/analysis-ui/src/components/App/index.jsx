import React from 'react';
import ReactDOM from 'react-dom';
import Image from 'react-image';
// From: https://github.com/react-component/slider
import Slider, { Range } from 'rc-slider';
import LineChart from 'react-linechart';
import TextareaAutosize from 'react-textarea-autosize';
import queryString from 'query-string';

import { Query } from 'react-apollo';
import gql from 'graphql-tag';
import _ from "lodash";

// Images from Test
import { imagey_1, imagey_2, imagey_3, imagey_4 } from './test/images';

// CSS Stuff 
import '../../css/app.css';
import 'rc-slider/assets/index.css';

const queryName = "getEvalAnalysis"
//TODO:  Update graphql so that we only return the values we need on the final page
const msc_eval = gql`
    query getEvalAnalysis($test: String!, $block: String!, $submission: String!, $performer: String! ){
        getEvalAnalysis(test: $test, block: $block, submission: $submission, performer: $performer) {
            block
            complexity
            ground_truth
            num_objects
            occluder
            performer
            plausibility
            scene
            submission
            test
            url_string
            voe_signal
        }
  }`;

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

export class EvalHeader extends React.Component {
    render() {
        return (
            <div className="header">
                <div className="title">Performer: { this.props.state.perf }</div>
                <div className="title">Submission: { this.props.state.subm }</div>
                <div className="title">Block: { this.props.state.block }</div>
                <div className="title">Test: { this.props.state.test }</div>
            </div>
        );
    }
}

class SceneScore extends React.Component {
    render() {
        return (
            <div className="sceneinfo">Scene: {this.props.eval.scene}  &nbsp;  Score: {this.props.eval.plausibility}</div>
        );
    }
}

class VoeChart extends React.Component {
    render() {
        return (
            <div className="voe_chart">
                <LineChart 
                    id={"line-chart-scene-" + this.props.eval.scene}
                    width={250}
                    height={200}
                    data={this.props.pointsData}
                    xLabel={"Frame"}
                    yLabel={"Plausibility"}
                    xMin={"0"}
                    xMax={"100"}
                    yMin={"0"}
                    yMax={"1.0"}
                    hidePoints={"true"}
                    ticks={5}
                />
            </div>
        );
    }
}

class Results extends React.Component {

    constructor(props) {
        super(props);
        this.state = {
            value: 0,
            valueStr: '',
        };
    }
    
    renderSquare(i) {}

    handleClick(i) {}

    onSliderChange = (value) => {
        this.setState( {
            value: value,
            valueStr: pad(value,3),
        })
    };

    render() {
        const evalsInOrder = _.sortBy(this.props.evals, "scene");
        this.state.data = [];

        const v = this.state.value;

        for(var i=0; i < evalsInOrder.length; i++) {
            var points = [];
            for(var j=1; j < Object.keys(evalsInOrder[i]["voe_signal"]).length + 1; j++) {
                points.push({x: j, y: evalsInOrder[i]["voe_signal"][j]});
            }

            this.state.data[i] = [{color: "steelblue", points: points}];
        }

        return (

            <div>
                <div className="intphys_img">
                    <img src={ imagey_1[v]} />
                    &nbsp;
                    <img src={ imagey_2[v] } />
                    &nbsp;
                    <img src={ imagey_3[v] } />
                    &nbsp;
                    <img src={ imagey_4[v] } />
                    &nbsp;
                </div>
                <div className="scene_div">
                    {evalsInOrder.map((item, key) =>
                        <SceneScore eval={item} key={key} />
                    )}
                </div>

                Frame: {v}

                <div className="slider">
                    <Slider value={this.state.value} onChange={this.onSliderChange} />
                </div>


                <div className="voe_div">
                    {evalsInOrder.map((item, key) =>
                        <VoeChart eval={item} key={key} pointsData={this.state.data[key]}/>
                    )}
                </div>                

                <div className="commentarea">
                    <TextareaAutosize minRows={4} defaultValue="Enter comments here.  Resize for more room"/>
                </div>
            </div>
        );
    }
}

export class App extends React.Component {

    // Assume that we are called with a URL like:
    // http://localhost:3000/app/?perf=TA1_group_test&subm=submission_0&block=O1&test=0001
    constructor(props) {
        super(props);

        this.state = queryString.parse(window.location.search);
    }
    
    render() {
        return (
            <Query query={msc_eval} variables={
                {"test": this.state.test, 
                "block": this.state.block, 
                "submission": this.state.subm, 
                "performer": this.state.perf
                }}>
            {
                ({ loading, error, data }) => {
                    if (loading) return <div>Loading ...</div> 
                    if (error) return <div>Error</div>
                    
                    const evals = data[queryName]

                    return (
                        <div>
                            <div className="layout">

                                <EvalHeader state={this.state}/>
                                
                                <div className="layout-board">
                                    <Results value={this.state} evals={evals}/>
                                </div>
                            </div>
                        </div>
                    )
                }
            }
            </Query>
        );
    }
}