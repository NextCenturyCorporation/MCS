import React from 'react';
//import Image from 'react-image';
// From: https://github.com/react-component/slider
import Slider from 'rc-slider';
import LineChart from 'react-linechart';
import _ from "lodash";
import { Query } from 'react-apollo';
import gql from 'graphql-tag';

const queryName = "getEvalAnalysis"
const imagesBucket = "https://intphys-images.s3.amazonaws.com/"

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

const SceneImage = ({ url }) => {
    const styles = {
      width: '250px',
      height: '250px',
      margin: '10px 25px'
    };
  
    return (
      <img className="scene-image" style={styles} src={url}/>
    );
  }

class Results extends React.Component {

    constructor(props) {
        super(props);
        this.state = {
            value: "001",
            valueStr: '',
        };
    }

    renderSquare(i) {}

    handleClick(i) {}

    onSliderChange = (value) => {
        let prefix = "";
        
        if(value < 10) { 
            prefix = "00";
        } else if (value < 100) {
            prefix = "0";
        }

        this.setState( {
            value: prefix + value,
            valueStr: pad(value,3),
        })
    };

    componentDidMount() {
        for(let j=1; j<= 4; j++) {
            for (let i =1; i <= 100; i++) {
                let prefix = "";

                if(i < 10) { 
                    prefix = "00";
                } else if (i < 100) {
                    prefix = "0";
                }

                const imageUrl = imagesBucket + this.props.value.block + "/" + this.props.value.test + "/" + j + "/scene/scene_" + prefix + i + ".png";
                new Image().src = imageUrl;
            }
        }
    }

    render() {
        return (
            <Query query={msc_eval} variables={
                {"test": this.props.value.test, 
                "block": this.props.value.block, 
                "submission": this.props.value.subm, 
                "performer": this.props.value.perf
                }}>
            {
                ({ loading, error, data }) => {
                    if (loading) return <div>Loading ...</div> 
                    if (error) return <div>Error</div>
                    
                    const evals = data[queryName]
                    const evalsInOrder = _.sortBy(evals, "scene");
                    this.state.data = [];

                    const v = this.state.value;
                    const scene1Path = imagesBucket + evalsInOrder[0]["block"] + "/" + evalsInOrder[0]["test"] + "/1/scene/scene_" + v + ".png"
                    const scene2Path = imagesBucket + evalsInOrder[1]["block"] + "/" + evalsInOrder[1]["test"] + "/2/scene/scene_" + v + ".png"
                    const scene3Path = imagesBucket + evalsInOrder[2]["block"] + "/" + evalsInOrder[2]["test"] + "/3/scene/scene_" + v + ".png"
                    const scene4Path = imagesBucket + evalsInOrder[3]["block"] + "/" + evalsInOrder[3]["test"] + "/4/scene/scene_" + v + ".png"

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
                                <SceneImage url={scene1Path}/>
                                <SceneImage url={scene2Path}/>
                                <SceneImage url={scene3Path}/>
                                <SceneImage url={scene4Path}/>
                            </div>
                            <div className="scene_div">
                                {evalsInOrder.map((item, key) =>
                                    <SceneScore eval={item} key={key} />
                                )}
                            </div>
            
                            Frame: {v}
            
                            <div className="slider">
                                <Slider value={parseInt(this.state.value)} onChange={this.onSliderChange} min={1}/>
                            </div>
            
            
                            <div className="voe_div">
                                {evalsInOrder.map((item, key) =>
                                    <VoeChart eval={item} key={key} pointsData={this.state.data[key]}/>
                                )}
                            </div>                
                        </div>
                    )
                }
            }
            </Query>
        );
    }
}

export default Results;