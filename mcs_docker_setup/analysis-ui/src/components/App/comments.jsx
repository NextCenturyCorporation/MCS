import React from 'react';
import AddCommentBlock from './addComment';
import DisplayComments from './commentsDisplay';

function CommentsComponent({state}) {
    const [needToRefetch, setNeedToRefetch] = React.useState(false);

    return(
        <div className="comments-holder">
            <DisplayComments value={state} needToRefetch={needToRefetch}/>
            <AddCommentBlock state={state} setNeedToRefetch={setNeedToRefetch}/>
        </div>
    );
}

export default CommentsComponent;