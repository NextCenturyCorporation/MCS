import React from 'react';
import { Query } from 'react-apollo';
import gql from 'graphql-tag';
import _ from "lodash";
import $ from 'jquery';
import FlagCheckboxMutation from './flagCheckboxMutation';

const historyQueryName = "getEvalHistory";
const sceneQueryName = "getEvalScene";
const moviesBucket = "https://evaluation-images.s3.amazonaws.com/eval-2-inphys-videos/"
const interactiveMoviesBucket = "https://evaluation-images.s3.amazonaws.com/eval-2/"
const topDownMoviesBucket = "https://evaluation-images.s3.amazonaws.com/eval-2-top-down/"
const movieExtension = ".mp4"
const sceneBucket = "https://evaluation-images.s3.amazonaws.com/eval-2-scenes/"
const sceneExtension = "-debug.json"

let currentState = {};
let currentStep = 0;

const PERFORMER_PREFIX_MAPPING = {
    "IBM-MIT-Harvard-Stanford": "mitibm_",
    "OPICS (OSU, UU, NYU)": "opics_",
    "MESS-UCBerkeley": "mess_",
    "IBM-MIT-Harvard-Stanford-2": "mitibm2_"
};

const mcs_history = gql`
    query getEvalHistory($testType: String!, $sceneNum: String!){
        getEvalHistory(testType: $testType, sceneNum: $sceneNum) {
            eval
            performer
            name
            test_type
            scene_num
            scene_part_num
            score
            steps
            flags
            step_counter
            category
            category_type
            category_pair
        }
  }`;

const mcs_scene= gql`
    query getEvalScene($testType: String!, $sceneNum: String!){
        getEvalScene(testType: $testType, sceneNum: $sceneNum) {
            name
            ceilingMaterial
            floorMaterial
            wallMaterial
            wallColors
            performerStart
            objects
            goal
            answer
            eval
            test_type
            scene_num
            scene_part_num
        }
  }`;
class Scenes extends React.Component {

    constructor(props) {
        super(props);
        this.state = {
            currentPerformerKey: 0,
            currentPerformer: props.value.performer !== undefined ? props.value.performer : "",
            currentSceneNum: props.value.scene_part_num !== undefined ? parseInt(props.value.scene_part_num) - 1 : 0,
            currentObjectNum: 0,
            flagRemove: false,
            flagInterest: false,
            testType: props.value.test_type,
            sceneNum: props.value.scene_num
        };
    }

    setInitialPerformer = (performer, firstEval) => {
        if(this.state.currentPerformer === "") {
            this.setState({
                currentPerformer: performer
            });
        }

        if(this.state.currentPerformer === "" && firstEval !== null && firstEval !== undefined) {
            this.setState({
                flagRemove: firstEval["flags"]["remove"],
                flagInterest: firstEval["flags"]["interest"]
            });
        }
    }

    changePerformer = (performerKey, performer) => {
        this.setState({ currentPerformerKey: performerKey, currentPerformer: performer});
    }

    changeScene = (sceneNum) => {
        this.setState({ currentSceneNum: sceneNum});
    }

    changeObjectDisplay = (objectKey) => {
        $('#object_button_' + this.state.currentObjectNum ).toggleClass( "active" );
        $('#object_button_' + objectKey ).toggleClass( "active" );

        this.setState({ currentObjectNum: objectKey});
    }

    convertArrayToString = (arrayToConvert) => {
        let newStr = "";
        for(let i=0; i < arrayToConvert.length; i++) {
            newStr = newStr + this.convertValueToString(arrayToConvert[i]);

            if(i < arrayToConvert.length -1) {
                newStr = newStr + ", ";
            }
        }

        return newStr;
    }

    convertObjectToString = (objectToConvert) => {
        let newStr = "";
        Object.keys(objectToConvert).forEach((key, index) => {
            newStr = newStr + key + ": " + this.convertValueToString(objectToConvert[key]);

            if(index < Object.keys(objectToConvert).length - 1) {
                newStr = newStr + ", ";
            }
        })

        return newStr;
    }

    convertValueToString = (valueToConvert) => {
        if(Array.isArray(valueToConvert) && valueToConvert !== null) {
            return this.convertArrayToString(valueToConvert);
        }

        if(typeof valueToConvert === 'object' && valueToConvert !== null) {
            return this.convertObjectToString(valueToConvert);
        }

        if(valueToConvert === true) {
            return "true";
        } 

        if(valueToConvert === false) {
            return "false";
        } 

        if(!isNaN(valueToConvert)) {
            return Math.floor(valueToConvert * 100) / 100;
        }

        return valueToConvert;
    }

    findObjectTabName = (sceneObject) => {
        if(sceneObject.shape !== undefined && sceneObject.shape !== null) {
            return sceneObject.shape;
        }

        if(sceneObject.id.indexOf('occluder_wall')) {
            return "occluder wall";
        }

        if(sceneObject.id.indexOf('occluder_pole')) {
            return "occluder pole";
        }

        return sceneObject.type;
    }

    checkSceneObjectKey = (scene, objectKey, key, labelPrefix = "") => {
        if(objectKey !== 'objects' && objectKey !== 'goal' && objectKey !== 'name') {
            return (
                <tr key={'scene_prop_' + key}>
                    <td className="bold-label">{labelPrefix + objectKey}:</td>
                    <td className="scene-text">{this.convertValueToString(scene[objectKey])}</td>
                </tr>
            );
        } else if(objectKey === 'goal') {
            return (
                Object.keys(scene["goal"]).map((goalObjectKey, goalKey) => 
                    this.checkSceneObjectKey(scene["goal"], goalObjectKey, goalKey, "goal."))
            );
        } else if(objectKey === 'name') {
            return (
                <tr key={'scene_prop_' + key}>
                    <td className="bold-label">{labelPrefix + objectKey}:</td>
                    <td className="scene-text">{this.convertValueToString(scene[objectKey])} (<a href={sceneBucket + scene[objectKey] + sceneExtension} download>Download Scene File</a>)</td>
                </tr>
            );
        }
    }

    highlightStep = (e) => {
        // First one is at 0.2 
        let currentTimeNum = Math.floor(document.getElementById("interactiveMoviePlayer").currentTime + 0.8);
        if(currentTimeNum !== currentStep) {
            $('#stepHolder' + currentStep ).toggleClass( "step-highlight" );
            currentStep = currentTimeNum;
            $('#stepHolder' + currentStep ).toggleClass( "step-highlight" );
            if(document.getElementById("stepHolder" + currentStep) !== null) {
                document.getElementById("stepHolder" + currentStep).scrollIntoView({behavior: "smooth", block: "nearest", inline: "start"});
            }
        }
    }

    initializeStepView = () => {
        $('#stepHolder' + currentStep ).toggleClass( "step-highlight" );
        currentStep = 0;
        $('#stepHolder' + currentStep ).toggleClass( "step-highlight" );
        if(document.getElementById("stepHolder" + currentStep) !== null) {
            document.getElementById("stepHolder" + currentStep).scrollIntoView({behavior: "smooth", block: "nearest", inline: "start"});
        }
    }

    goToVideoLocation = (jumpTime) => {
        if( document.getElementById("interactiveMoviePlayer") !== null) {
            $('#stepHolder' + currentStep ).toggleClass( "step-highlight" );
            currentStep = jumpTime;
            document.getElementById("interactiveMoviePlayer").currentTime = jumpTime;
            $('#stepHolder' + currentStep ).toggleClass( "step-highlight" );
        }
    }

    render() {
        return (
            <Query query={mcs_history} variables={
                {"testType": this.props.value.test_type, 
                "sceneNum": this.props.value.scene_num
                }} fetchPolicy='network-only'>
            {
                ({ loading, error, data }) => {
                    if (loading) return <div>Loading ...</div> 
                    if (error) return <div>Error</div>
                    
                    const evals = data[historyQueryName];
                    let scenesByPerformer = _.sortBy(evals, "scene_part_num");
                    scenesByPerformer = _.groupBy(scenesByPerformer, "performer");
                    let performerList = Object.keys(scenesByPerformer);
                    this.setInitialPerformer(performerList[0], evals[0]);

                    if(performerList.length > 0) {
                        return (
                            <Query query={mcs_scene} variables={
                                {"testType": this.props.value.test_type, 
                                "sceneNum": this.props.value.scene_num
                                }}>
                            {
                                ({ loading, error, data }) => {
                                    if (loading) return <div>Loading ...</div> 
                                    if (error) return <div>Error</div>
                                    
                                    const scenes = data[sceneQueryName];
                                    const scenesInOrder = _.sortBy(scenes, "scene_part_num");
                                    this.initializeStepView();

                                    if(scenesInOrder.length > 0) {
                                        return (
                                            <div>
                                                <div className="flags-holder">
                                                    <FlagCheckboxMutation state={this.state} currentState={currentState}/>
                                                </div>
                                                { (scenesByPerformer[this.state.currentPerformer][0]["category"] === "observation") && 
                                                    <div>
                                                        <div className="movie-holder">
                                                            <div className="movie-left-right">
                                                                <div className="movie-text"><b>Scene 1:</b>&nbsp;&nbsp;{scenesInOrder[0].answer.choice}</div>
                                                                <div className="movie-text"><b>Scene 3:</b>&nbsp;&nbsp;{scenesInOrder[2].answer.choice}</div>
                                                            </div>
                                                            <div className="movie-center">
                                                                <video src={moviesBucket + this.props.value.test_type + "-" + this.props.value.scene_num + movieExtension} width="600" height="400" controls="controls" autoPlay={false} />
                                                            </div>
                                                            <div className="movie-left-right">
                                                                <div className="movie-text"><b>Scene 2:</b>&nbsp;&nbsp;{scenesInOrder[1].answer.choice}</div>
                                                                <div className="movie-text"><b>Scene 4:</b>&nbsp;&nbsp;{scenesInOrder[3].answer.choice}</div>
                                                            </div>
                                                        </div>
                                                    </div> 
                                                }
                                                <div className="scores_header">
                                                    <h3>Scores</h3>
                                                </div>
                                                <div className="performer-group btn-group" role="group">
                                                    {performerList.map((performer, key) =>
                                                        <button className={performer === this.state.currentPerformer ? 'btn btn-primary active' : 'btn btn-secondary'} id={'toggle_performer_' + key} key={'toggle_' + performer} type="button" onClick={() => this.changePerformer(key, performer)}>{performer}</button>
                                                    )}
                                                </div>
                                                <div className="score-table-div">
                                                    <table className="score-table">
                                                        <thead>
                                                            <tr>
                                                                <th>Scene Number</th>
                                                                <th>Answer</th>
                                                                <th>Score</th>
                                                                <th>Adjusted Confidence</th>
                                                                <th>Confidence</th>
                                                                <th>MSE</th>
                                                            </tr>
                                                        </thead>
                                                        <tbody>
                                                            {scenesByPerformer[this.state.currentPerformer].map((scoreObj, key) => 
                                                                <tr key={'peformer_score_row_' + key}>
                                                                    <td>{scoreObj.scene_part_num}</td>
                                                                    <td>{scoreObj.score.classification}</td>
                                                                    <td>{scoreObj.score.score_description}</td>
                                                                    <td>{scoreObj.score.adjusted_confidence}</td>
                                                                    <td>{scoreObj.score.confidence}</td>
                                                                    <td>{scoreObj.score.mse_loss}</td>
                                                                </tr>
                                                            )}
                                                        </tbody>
                                                    </table>
                                                </div>
                                                <div className="scenes_header">
                                                    <h3>Scenes</h3>
                                                </div>
                                                <div className="scene-group btn-group" role="group">
                                                    {scenesInOrder.map((scene, key) =>
                                                        <button key={"scene_button_" + key} className={this.state.currentSceneNum === key ? 'btn btn-primary active' : 'btn btn-secondary'} id={"scene_btn_" + key} type="button" onClick={() => this.changeScene(key)}>Scene {key+1}</button>
                                                    )}
                                                </div>
                                                    { (scenesByPerformer[this.state.currentPerformer][0]["category"] === "interactive") && 
                                                        <div className="movie-steps-holder">
                                                            <div className="interactive-movie-holder">
                                                                <video id="interactiveMoviePlayer" src={interactiveMoviesBucket + PERFORMER_PREFIX_MAPPING[this.state.currentPerformer] + this.props.value.test_type + "-" + this.props.value.scene_num + "-" + (this.state.currentSceneNum+1) + movieExtension} width="500" height="350" controls="controls" autoPlay={false} onTimeUpdate={this.highlightStep}/>
                                                            </div>
                                                            <div className="steps-holder">
                                                                <h5>Peformer Steps:</h5>
                                                                <div className="steps-container">
                                                                        <div id="stepHolder0" className="step-div step-highlight" onClick={() => this.goToVideoLocation(0)}>0: Starting Position</div>
                                                                    {scenesByPerformer[this.state.currentPerformer][this.state.currentSceneNum].steps.map((stepObject, key) => 
                                                                        <div key={"step_div_" + key} id={"stepHolder" + (key+1)} className="step-div" onClick={() => this.goToVideoLocation(key+1)}>
                                                                            {stepObject.stepNumber + ": " + stepObject.action + " (" + this.convertValueToString(stepObject.args) + ") - " + stepObject.output.return_status}
                                                                        </div>
                                                                    )}
                                                                </div>
                                                            </div>
                                                            <div className="top-down-holder">
                                                                <video id="interactiveMoviePlayer" src={topDownMoviesBucket + PERFORMER_PREFIX_MAPPING[this.state.currentPerformer] + this.props.value.test_type + "-" + this.props.value.scene_num + "-" + (this.state.currentSceneNum+1) + movieExtension} width="500" height="350" controls="controls" autoPlay={false}/>
                                                            </div>
                                                        </div> 
                                                    }
                                                <div className="scene-table-div">
                                                    <table>
                                                        <tbody>
                                                            {Object.keys(scenesInOrder[this.state.currentSceneNum]).map((objectKey, key) => 
                                                                this.checkSceneObjectKey(scenesInOrder[this.state.currentSceneNum], objectKey, key))}
                                                        </tbody>
                                                    </table>
                                                    <div className="objects_scenes_header">
                                                        <h5>Objects in Scene</h5>
                                                    </div>
                                                    <div className="object-nav">
                                                        <ul className="nav nav-tabs">
                                                            {scenesInOrder[this.state.currentSceneNum].objects.map((sceneObject, key) => 
                                                                <li className="nav-item" key={'object_tab_' + key}>
                                                                    <button id={'object_button_' + key} className={key === 0 ? 'nav-link active' : 'nav-link'} onClick={() => this.changeObjectDisplay(key)}>{this.findObjectTabName(sceneObject)}</button>
                                                                </li>
                                                            )}
                                                        </ul>
                                                    </div>
                                                    <div className="object-contents">
                                                        <table>
                                                            <tbody>
                                                                {Object.keys(scenesInOrder[this.state.currentSceneNum].objects[this.state.currentObjectNum]).map((objectKey, key) => 
                                                                    <tr key={'object_tab_' + key}>
                                                                        <td className="bold-label">{objectKey}:</td>
                                                                        <td className="scene-text">{this.convertValueToString(scenesInOrder[this.state.currentSceneNum].objects[this.state.currentObjectNum][objectKey])}</td>
                                                                    </tr>
                                                                )}
                                                            </tbody>
                                                        </table>
                                                    </div>        
                                                </div>
                                            </div>
                                        )
                                    }  else {
                                        return <div>No Results available for these choices.</div>
                                    }
                                }
                            }
                            </Query>
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

export default Scenes;