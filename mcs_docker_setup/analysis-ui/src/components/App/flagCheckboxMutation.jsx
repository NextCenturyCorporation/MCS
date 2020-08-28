import React from 'react';
import { useMutation } from 'react-apollo';
import gql from 'graphql-tag';

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

const flagRemoveMutation = gql`
    mutation updateSceneHistoryRemoveFlag($testType: String!, $sceneNum: String!, $flagRemove: Boolean!) {
        updateSceneHistoryRemoveFlag(testType: $testType, sceneNum: $sceneNum, flagRemove: $flagRemove) {
            total
        }
    }
`;

const flagInterestMutation = gql`
    mutation updateSceneHistoryInterestFlag($testType: String!, $sceneNum: String!, $flagInterest: Boolean!) {
        updateSceneHistoryInterestFlag(testType: $testType, sceneNum: $sceneNum, flagInterest: $flagInterest) {
            total
        }
    }
`;

const FlagCheckboxMutation = ({state, currentState}) => {
    const [updateRemoveFlags] = useMutation(flagRemoveMutation);
    const [updateInterestFlags] = useMutation(flagInterestMutation);

    const updateRemoveFlag = (evt) => {
        state.flagRemove = state.flagRemove  ? false : true;
        mutateRemoveFlagUpdate();
    }

    const updateInterestFlag = (evt) => {
        state.flagInterest = state.flagInterest ? false : true;
        mutateInterestFlagUpdate();
    }

    const mutateRemoveFlagUpdate = () => {
        updateRemoveFlags({
                variables: {
                    testType: state.testType,
                    sceneNum: state.sceneNum,
                    flagRemove: state.flagRemove
            }, refetchQueries: { 
                query: mcs_history, 
                variables:{"testType": currentState.testType, "sceneNum": currentState.sceneNum}
            }
        });
    }

    const mutateInterestFlagUpdate = () => {
        updateInterestFlags({
                variables: {
                    testType: state.testType,
                    sceneNum: state.sceneNum,
                    flagInterest: state.flagInterest  
            }, refetchQueries: { 
                query: mcs_history, 
                variables:{"testType": currentState.testType, "sceneNum": currentState.sceneNum}
            }
        });
    }

    return (
        <div className="checkbox-holder">
              <div className="form-check">
                  <label className="form-check-label">
                      <input type="checkbox" id="flagCheckRemove" className="form-check-input" name="Flag for removal" checked={state.flagRemove} onChange={updateRemoveFlag}/>
                      Flag for removal
                  </label>
              </div>
              <div className="form-check">
                  <label className="form-check-label">
                      <input type="checkbox" id="flagCheckInterest" className="form-check-input" mame="Flag for interest" checked={state.flagInterest} onChange={updateInterestFlag}/>
                      Flag for interest
                  </label>
              </div>
        </div>
    )
}

export default FlagCheckboxMutation;