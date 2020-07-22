import React from 'react';
import { Query } from 'react-apollo';
import gql from 'graphql-tag';
import _ from "lodash";
import $ from 'jquery';

const historyQueryName = "getEvalHistory";
const sceneQueryName = "getEvalScene";
const moviesBucket = "https://evaluation-images.s3.amazonaws.com/eval-2-inphys-videos/"
const movieExtension = ".mp4"

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
            currentPerformer: "",
            currentSceneNum: props.value.scene_part_num !== undefined ? parseInt(props.value.scene_part_num) - 1 : 0,
            currentObjectNum: 0
        };
    }

    setInitialPerformer = (performer) => {
        if(this.state.currentPerformer === "") {
            this.setState({currentPerformer: performer});
        }
    }

    changePerformer = (performerKey, performer) => {
        $('#toggle_performer_' + this.state.currentPerformerKey ).toggleClass( "btn-primary" );
        $('#toggle_performer_' + this.state.currentPerformerKey ).toggleClass( "btn-secondary" );
        
        $('#toggle_performer_' + performerKey ).toggleClass( "btn-secondary" );
        $('#toggle_performer_' + performerKey).toggleClass( "btn-primary" );

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

    render() {
        return (
            <Query query={mcs_history} variables={
                {"testType": this.props.value.test_type, 
                "sceneNum": this.props.value.scene_num
                }}>
            {
                ({ loading, error, data }) => {
                    if (loading) return <div>Loading ...</div> 
                    if (error) return <div>Error</div>
                    
                    const evals = data[historyQueryName];
                    let scenesByPerformer = _.sortBy(evals, "scene_part_num");
                    scenesByPerformer = _.groupBy(scenesByPerformer, "performer");
                    let performerList = Object.keys(scenesByPerformer);
                    this.setInitialPerformer(performerList[0]);

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

                                    if(scenesInOrder.length > 0) {
                                        return (
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
                                                <div className="scores_header">
                                                    <h3>Scores</h3>
                                                </div>
                                                <div className="performer-group btn-group" role="group">
                                                    {performerList.map((performer, key) =>
                                                        <button className={key === 0 ? 'btn btn-primary active' : 'btn btn-secondary'} id={'toggle_performer_' + key} key={'toggle_' + performer} type="button" onClick={() => this.changePerformer(key, performer)}>{performer}</button>
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
                                                    <button className={this.state.currentSceneNum === 0 ? 'btn btn-primary active' : 'btn btn-secondary'} id="scene_btn_0" type="button" onClick={() => this.changeScene(0)}>Scene 1</button>
                                                    <button className={this.state.currentSceneNum === 1 ? 'btn btn-primary active' : 'btn btn-secondary'} id="scene_btn_1" type="button" onClick={() => this.changeScene(1)}>Scene 2</button>
                                                    <button className={this.state.currentSceneNum === 2 ? 'btn btn-primary active' : 'btn btn-secondary'} id="scene_btn_2" type="button" onClick={() => this.changeScene(2)}>Scene 3</button>
                                                    <button className={this.state.currentSceneNum === 3 ? 'btn btn-primary active' : 'btn btn-secondary'} id="scene_btn_3" type="button" onClick={() => this.changeScene(3)}>Scene 4</button>
                                                </div>
                                                <div className="scene-table-div">
                                                    <table>
                                                        <tbody>
                                                            <tr>
                                                                <td className="bold-label">Ceiling Material:</td>
                                                                <td className="scene-text">{scenesInOrder[this.state.currentSceneNum].ceilingMaterial}</td>
                                                            </tr>
                                                            <tr>
                                                                <td className="bold-label">Floor Material:</td>
                                                                <td className="scene-text">{scenesInOrder[this.state.currentSceneNum].floorMaterial}</td>
                                                            </tr>
                                                            <tr>
                                                                <td className="bold-label">Wall Material:</td>
                                                                <td className="scene-text">{scenesInOrder[this.state.currentSceneNum].wallMaterial}</td>
                                                            </tr>
                                                            <tr>
                                                                <td className="bold-label">Wall Colors:</td>
                                                                <td className="scene-text">{this.convertArrayToString(scenesInOrder[this.state.currentSceneNum].wallColors)}</td>
                                                            </tr>
                                                            <tr>   
                                                                <td className="bold-label">Performer Start:</td>
                                                                <td className="scene-text">Position (x: {scenesInOrder[this.state.currentSceneNum].performerStart.position.x}, 
                                                                    y: {scenesInOrder[this.state.currentSceneNum].performerStart.position.y}, z: {scenesInOrder[this.state.currentSceneNum].performerStart.position.z}), 
                                                                    Rotation: (y: {scenesInOrder[this.state.currentSceneNum].performerStart.rotation.y})</td>
                                                            </tr>
                                                            <tr>
                                                                <td className="bold-label">Category:</td>
                                                                <td className="scene-text">{scenesInOrder[this.state.currentSceneNum].goal.category}</td>
                                                            </tr>
                                                            <tr>
                                                                <td className="bold-label">Domain List:</td>
                                                                <td className="scene-text">{this.convertArrayToString(scenesInOrder[this.state.currentSceneNum].goal.domain_list)}</td>
                                                            </tr>
                                                            <tr>
                                                                <td className="bold-label">Type List:</td>
                                                                <td className="scene-text">{this.convertArrayToString(scenesInOrder[this.state.currentSceneNum].goal.type_list)}</td>
                                                            </tr>
                                                            <tr>
                                                                <td className="bold-label">Task List:</td>
                                                                <td className="scene-text">{this.convertArrayToString(scenesInOrder[this.state.currentSceneNum].goal.task_list)}</td>
                                                            </tr>
                                                            <tr>
                                                                <td className="bold-label">Info List:</td>
                                                                <td className="scene-text">{this.convertArrayToString(scenesInOrder[this.state.currentSceneNum].goal.info_list)}</td>
                                                            </tr>
                                                            <tr>
                                                                <td className="bold-label">Correct Answer:</td>
                                                                <td className="scene-text">{scenesInOrder[this.state.currentSceneNum].answer.choice}</td>
                                                            </tr>
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