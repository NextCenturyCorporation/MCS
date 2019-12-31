import React from 'react';
import _ from "lodash";
import { Query } from 'react-apollo';
import gql from 'graphql-tag';
import SceneSlider from './sceneSlider';
import SceneImage from './sceneImage';
import PlausabilityGraph from './plausabilityGraph';

const queryName = "getEvalAnalysis"
const imagesBucket = "https://intphys-images.s3.amazonaws.com/"

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

class Results extends React.Component {

    constructor(props) {
        super(props);
        this.state = {
            value: "001"
        };
    }

    getPrefix = (value) => {
        let prefix = "";
        
        if(value < 10) { 
            prefix = "00";
        } else if (value < 100) {
            prefix = "0";
        }

        return prefix;
    }

    onSliderChange = (value) => {
        this.setState( {
            value: this.getPrefix(value) + value
        })
    };

    componentDidMount() {
        for(let j=1; j<= 4; j++) {
            for (let i =1; i <= 100; i++) {
                const imageUrl = imagesBucket + this.props.value.block + "/" + this.props.value.test + "/" + j + "/scene/scene_" + this.getPrefix(i) + i + ".png";
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
                    let pointsData = [];

                    if(evalsInOrder.length > 0) {

                        for(var i=0; i < evalsInOrder.length; i++) {
                            var points = [];
                            for(var j=1; j < Object.keys(evalsInOrder[i]["voe_signal"]).length + 1; j++) {
                                points.push({x: j, y: evalsInOrder[i]["voe_signal"][j]});
                            }

                            let hue = Math.floor(Math.random() * (350 - 10 + 1)) + 10;

                            pointsData.push({id: "Scene " + (i+1), color: "hsla(" + hue + ", 70%, 50%, 0)", data: points});
                        }

                        return (
                            <div>
                                <SceneSlider state={this.state} onChange={this.onSliderChange}/>
                                <SceneImage state={this.state} evals={evalsInOrder} imagesBucket={imagesBucket}/>
                
                                <div className="voe_div">
                                    <PlausabilityGraph pointsData={pointsData} state={this.state}/>
                                </div>                
                            </div>
                        )
                    }  else {
                        return <div>No Results available for these choices.</div>
                    }
                }
            }
            </Query>
        );
    }
}

export default Results;