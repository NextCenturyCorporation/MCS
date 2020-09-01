import React from 'react';
import _ from "lodash";
import { Query } from 'react-apollo';
import gql from 'graphql-tag';

// For Eval 1 Comments
const queryName = "getComments";
const GET_COMMENTS = gql`
    query getComments($test: String!, $block: String!, $submission: String!, $performer: String! ){
        getComments(test: $test, block: $block, submission: $submission, performer: $performer) {
            id
            block
            performer
            submission
            test
            createdDate
            text
            userName
        }
  }`;

// For Comments Eval 2 Going forward
const commentsQueryName = "getCommentsByTestAndScene";
const GET_COMMENTS_BY_TEST_AND_SCENE = gql`
    query getCommentsByTestAndScene($testType: String!, $sceneNum: String!){
        getCommentsByTestAndScene(testType: $testType, sceneNum: $sceneNum) {
            id
            test_type
            scene_num
            createdDate
            text
            userName
        }
  }`;

const IndividualComment = ({comments}) => {
    const commentsInOrder = _.sortBy(comments, "createdDate");
        
    return (
        <div className="comment-container">
            <h2>Comments</h2>
            {commentsInOrder.length > 0 && commentsInOrder.map((item, key) =>
                <div key={key} className="comment-display"><span className="comment-date">{item.createdDate}:</span>
                &nbsp;{item.userName} - {item.text}</div>
            )}

            {commentsInOrder.length === 0 && 
                <div>There are no comments yet for this test.</div>
            }
        </div>
    );
}

const CommentBlock = ({props, qName, queryType, queryVars}) => {
    return (
        <Query query={queryType} variables={queryVars} fetchPolicy={props.needToRefetch ? 'network-only' : 'cache-first'}>
        {
            ({ loading, error, data }) => {
                if (loading) return <div>No comments yet</div> 
                if (error) return <div>Error</div>
                
                const comments = data[qName]

                return (
                    <IndividualComment comments={comments}/>
                )
            }
        }
        </Query>
    );
}

const CommentBlockHolder = ({props}) => {
    if(props.value.test_type !== undefined && props.value.test_type !== null) {
        const queryVars = {
            "testType": props.value.test_type, 
            "sceneNum": props.value.scene_num
        };

        return (
            <CommentBlock props={props} qName={commentsQueryName} queryType={GET_COMMENTS_BY_TEST_AND_SCENE} queryVars={queryVars}/>
        );
    } else {
        const queryVars = {
            "test": props.value.test, 
            "block": props.value.block, 
            "submission": props.value.subm, 
            "performer": props.value.perf
        };

        return (
            <CommentBlock props={props} qName={queryName} queryType={GET_COMMENTS} queryVars={queryVars}/>
        );
    }
}

class DisplayComments extends React.Component {

    render() {
        return (
            <CommentBlockHolder props={this.props}/>
        );
    }
}

export {GET_COMMENTS};
export default DisplayComments;