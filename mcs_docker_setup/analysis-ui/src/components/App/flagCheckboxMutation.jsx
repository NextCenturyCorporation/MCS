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

const flagMutation = gql`
    mutation updateSceneHistoryFlags($testType: String!, $sceneNum: String!, $flagRemove: Boolean!, $flagInterest: Boolean!) {
        updateSceneHistoryFlags(testType: $testType, sceneNum: $sceneNum, flagRemove: $flagRemove, flagInterest: $flagInterest) {
            total
        }
    }
`;

const FlagCheckboxMutation = ({state, currentState}) => {
    const [updateFlags] = useMutation(flagMutation);

    const updateRemoveFlag = (evt) => {
        state.flagRemove = state.flagRemove  ? false : true;
        mutateFlagUpdate();
    }

    const updateInterestFlag = (evt) => {
        state.flagInterest = state.flagInterest ? false : true;
        mutateFlagUpdate();
    }

    const mutateFlagUpdate = () => {
        updateFlags({
                variables: {
                    testType: state.testType,
                    sceneNum: state.sceneNum,
                    flagRemove: state.flagRemove,
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