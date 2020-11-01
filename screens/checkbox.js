import React from 'react';
import { StyleSheet, Text, View, Image, Button, ActivityIndicator} from 'react-native';
import { AppLoading } from 'expo';
import * as Font from 'expo-font';
import { TextInput, TouchableOpacity } from 'react-native-gesture-handler';
import DropDownPicker from 'react-native-dropdown-picker';
import { CheckBox, Icon } from 'react-native-elements'
import { Camera } from 'expo-camera';
import * as Permissions from 'expo-permissions';
import { Audio } from 'expo-av';
import * as FileSystem from "expo-file-system";
import Svg, { Circle, Line, Polyline } from 'react-native-svg';

var imgdata=null;
var url=null;
var cUrl=null;
var pUrl=null;
var x=[];
var index = [0,0,0,0,0,0,0,0,0];
let customFonts  = {
    'FuturaH': require('../assets/fonts/futurah.ttf'),
    'FuturaL': require('../assets/fonts/futural.ttf'),
  };

  const recordingOptions = {
    // android not currently in use. Not getting results from speech to text with .m4a
    // but parameters are required
    android: {
        extension: '.m4a',
        outputFormat: Audio.RECORDING_OPTION_ANDROID_OUTPUT_FORMAT_MPEG_4,
        audioEncoder: Audio.RECORDING_OPTION_ANDROID_AUDIO_ENCODER_AAC,
        sampleRate: 44100,
        numberOfChannels: 2,
        bitRate: 128000,
    },
    ios: {
        extension: '.wav',
        audioQuality: Audio.RECORDING_OPTION_IOS_AUDIO_QUALITY_HIGH,
        sampleRate: 44100,
        numberOfChannels: 1,
        bitRate: 128000,
        linearPCMBitDepth: 16,
        linearPCMIsBigEndian: false,
        linearPCMIsFloat: false,
    },
};


export default class Check extends React.Component  {
  state = {
    fontsLoaded: false,
    method: null,
    face: false,
    hand: false,
    voice: false,
    pattern: false,
    index:[[0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0]],
    path: [],
    bgHand: 'white',
    bgPattern: 'white',
    bgFace: 'white',
    bgVoice: 'white',
    isFetching: false,
    isRecording: false,
    patternstr: '',
    
  };
  
  async _loadFontsAsync() {
    await Font.loadAsync(customFonts);
    this.setState({ fontsLoaded: true });
  }

  

  async componentDidMount() {
    this._loadFontsAsync();
    const { status } = await Permissions.askAsync(Permissions.CAMERA);
    this.setState({ hasCameraPermission: status === 'granted' });
    const { mic } = await Permissions.askAsync(Permissions.AUDIO_RECORDING);
    
  }

  registerUser(){
    fetch('https://us-central1-aiot-fit-xlab.cloudfunctions.net/autoplaygeneral', {
        method: 'POST',
        headers: {
        'Content-Type': 'application/json',
        },
        body: JSON.stringify({"action": "register", "lat" : 2.2222, "lon": 45.225, "email":"e@mail.com", "password" : "somepasswordhere", "spotify": "2222222"})
})
    .then((response) => response.json())
    .then((responseJson) => {
console.log(responseJson);
    })
    .catch((error) => {
        console.error(error);
    });
  }
  

  startRecording = async () => {
    const { status } = await Permissions.getAsync(Permissions.AUDIO_RECORDING);
    if (status !== 'granted') return;

    this.setState({ isRecording: true });
    await Audio.setAudioModeAsync({
        allowsRecordingIOS: true,
        interruptionModeIOS: Audio.INTERRUPTION_MODE_IOS_DO_NOT_MIX,
        playsInSilentModeIOS: true,
        shouldDuckAndroid: true,
        interruptionModeAndroid: Audio.INTERRUPTION_MODE_ANDROID_DO_NOT_MIX,
        playThroughEarpieceAndroid: true,
    });
    const recording = new Audio.Recording();

    try {
        await recording.prepareToRecordAsync(recordingOptions);
        await recording.startAsync();
    } catch (error) {
        console.log(error);
        this.stopRecording();
    }

    this.recording = recording;
}

stopRecording = async () => {
    this.setState({ isRecording: false });
    try {
        await this.recording.stopAndUnloadAsync();
       const info = await FileSystem.getInfoAsync(this.recording.getURI());
        console.log(`FILE INFO: ${JSON.stringify(info)}`);
        const uri = info.uri;
        const formData = new FormData();
            formData.append('file', {
                uri,
                type: 'audio/x-wav',
                name: 'audiopass'
            });
            const response = await fetch('https://01bb231cc40bf1a2608e3a9aaa622815.m.pipedream.net', {
                method: 'POST',
                body: formData
            });
            const data = await response.json();
            console.log(data);
            
    
    } catch (error) {
        console.log('There was an error reading file', error);
            this.stopRecording();
            this.resetRecording();
    }
}

resetRecording = () => {
    this.deleteRecordingFile();
    this.recording = null;
}

handleOnPressIn = () => {
    this.startRecording();
    console.log('Start')
}

handleOnPressOut = () => {
    this.stopRecording();
    console.log('Stopped');
    this.setState({bgVoice:'green'}); 
    this.setState({voice:false});
    
}

  

  render(){



    const { hasCameraPermission } = this.state;
    const { isRecording, isFetching } = this.state;
    const {ref} = this.state;
    let { image } = this.state;
    const takePicture = async () => {
   
            const options = {quality: 0.5, base64: true};
            imgdata = await this.camera.takePictureAsync(options);
            url=imgdata.uri;
            console.log('Image Captured');
            console.log(url);
            
            let base64Img = `data:image/jpg;base64,${imgdata.base64}`
      
            
           let cloudinary = 'https://api.cloudinary.com/v1_1/diywehkap/image/upload';
        
            let data = {
              "file": base64Img,
              "upload_preset": "hm4fkyir",
            }
            fetch(cloudinary, {
              body: JSON.stringify(data),
              headers: {
                'content-type': 'application/json'
              },
              method: 'POST',
            }).then(async r => {
              let data = await r.json()
              cUrl=data.secure_url;
              pUrl=cUrl.toString();
              console.log(pUrl);
              x=1;
              return pUrl
          }).catch(err=>console.log(err));
        }
    if (this.state.fontsLoaded) {
    return (
    <View style={styles.container}>
     
      <Text style={{position:'relative',fontSize:30,marginTop:'10%', textAlign:'center', color:'#364f6b', fontFamily:'FuturaH'}}>Complete Sign Up</Text>
      <Text style={{position:'relative',fontSize:20,marginTop:'5%', textAlign:'center', color:'#364f6b', fontFamily:'FuturaL'}}>Select secondary authentication methods</Text>
      <CheckBox
  center
  title='Hand Gesture'
  checkedIcon='check-circle'
  uncheckedIcon='circle-o'
  checked={this.state.hand}
  containerStyle={{backgroundColor:this.state.bgHand}}
  onPress={() => {this.setState({hand: !this.state.hand});}}
/>

<CheckBox
  center
  title='Voice Password'
  checkedIcon='check-circle'
  uncheckedIcon='circle-o'
  checked={this.state.voice}
  containerStyle={{backgroundColor:this.state.bgVoice}}
  onPress={() => {this.setState({voice: !this.state.voice});}}
/> 
<CheckBox
  center
  title='Pattern'
  checkedIcon='check-circle'
  uncheckedIcon='circle-o'
  checked={this.state.pattern}
  containerStyle={{backgroundColor:this.state.bgPattern}}
  onPress={() => this.setState({pattern: !this.state.pattern})}
/> 
<CheckBox
  center
  title='Face Gesture'
  checkedIcon='check-circle'
  uncheckedIcon='circle-o'
  checked={this.state.face}
  containerStyle={{backgroundColor:this.state.bgFace}}
  onPress={() => this.setState({face: !this.state.face})}
/>
{hasCameraPermission && !this.state.pattern && !this.state.voice && 
 <Camera style={{ flex: 0.5, position:'absolute', height:500, width:400, marginTop:'90%' }} type={this.state.type} ref={ref => {this.camera = ref;}}>
 <View
   style={{
     flex: 1,
     backgroundColor: 'transparent',
     flexDirection: 'row',
   }}>
   <TouchableOpacity
     style={{
       flex: 0.1,
       alignSelf: 'flex-end',
       alignItems: 'center',
     }}
     onPress={() => {
       this.setState({
         type:
           this.state.type === Camera.Constants.Type.back
             ? Camera.Constants.Type.front
             : Camera.Constants.Type.back,
       });
     }}>
     <Text style={{ fontSize: 18, marginBottom: 10, color: 'white' }}> Flip </Text>
   </TouchableOpacity>
 </View>
</Camera>}
{this.state.voice &&
<>
{isRecording &&
                       
        <Icon name="mic" size={100} color="#ED008C" />}
                      
                    {!isRecording &&
                        <Icon name="mic" size={100} color="#ED008C" />
                    }
                    <TouchableOpacity
                        style={styles.button}
                        onPressIn={this.handleOnPressIn}
                        onPressOut={this.handleOnPressOut}
                    >
                        {isFetching && <ActivityIndicator color="#ffffff" />}
                        {!isFetching && <Text style={{fontFamily:'FuturaH', textAlign:'center', fontSize:20, color:'white', backgroundColor:'#ED008C', paddingHorizontal:'5%'}}>Hold to record voice password</Text>}
                    </TouchableOpacity></>}
{this.state.pattern &&
  <View style={{paddingHorizontal:'2%'}}>
  <Svg height="70%" width="70%" viewBox="0 0 100 100" style={{alignSelf:'center'}} >
<Circle cx="10" cy="10" r="5" stroke="blue" strokeWidth={index[0].toString()} fill="#ED008C" onPress={()=>{x.push(0); this.setState({path:x}); index[0]++; console.log(index)}}/> 
{!this.state.path &&   <Line x1="10" y1="10" x2="50" y2="10" stroke="#969" />}
{!this.state.path &&   <Line x1="10" y1="10" x2="10" y2="50" stroke="#969" />}
{!this.state.path &&   <Line x1="10" y1="10" x2="50" y2="50" stroke="#969" />}
<Circle cx="50" cy="10" r="5" stroke="blue" strokeWidth={index[1].toString()}  fill="#ED008C"  onPress={()=>{x.push(1); this.setState({path:x}); index[1]++; console.log(x)}} />
{!this.state.path &&   <Line x1="50" y1="10" x2="90" y2="10" stroke="#969" />}
{!this.state.path &&   <Line x1="50" y1="10" x2="50" y2="50" stroke="#969" />}
{!this.state.path &&   <Line x1="50" y1="10" x2="90" y2="50" stroke="#969" />}
{!this.state.path &&   <Line x1="50" y1="10" x2="10" y2="50" stroke="#969" />}
<Circle cx="90" cy="10" r="5" stroke="blue" strokeWidth={index[2].toString()}  fill="#ED008C"  onPress={()=>{x.push(2); this.setState({path:x}); index[2]++; console.log(x)}}/>
{!this.state.path &&   <Line x1="90" y1="10" x2="90" y2="50" stroke="#969" />}
{!this.state.path &&   <Line x1="90" y1="10" x2="50" y2="50" stroke="#969" />}

<Circle cx="10" cy="50" r="5" stroke="blue" strokeWidth={index[3].toString()}  fill="#ED008C"  onPress={()=>{x.push(3);this.setState({path:x});index[3]++;console.log(x)}} />
{!this.state.path &&   <Line x1="10" y1="50" x2="50" y2="50" stroke="#96A" />}
{!this.state.path &&   <Line x1="10" y1="50" x2="10" y2="90" stroke="#96A" />}
{!this.state.path &&   <Line x1="10" y1="50" x2="50" y2="90" stroke="#96A" />}
<Circle cx="50" cy="50" r="5" stroke="blue" strokeWidth={index[4].toString()} fill="#ED008C"  onPress={()=>{x.push(4); this.setState({path:x}); index[4]++; console.log(x)}} />
{!this.state.path &&   <Line x1="50" y1="50" x2="50" y2="90" stroke="#96A" />}
{!this.state.path &&   <Line x1="50" y1="50" x2="90" y2="50" stroke="#96A" />}
{!this.state.path &&   <Line x1="50" y1="50" x2="90" y2="90" stroke="#96A" />}
{!this.state.path &&   <Line x1="50" y1="50" x2="10" y2="90" stroke="#96A" />}
<Circle cx="90" cy="50" r="5" stroke="blue" strokeWidth={index[5].toString()}  fill="#ED008C"  onPress={()=>{x.push(5); this.setState({path:x}); index[5]++; console.log(x)}}/>
{!this.state.path &&   <Line x1="90" y1="50" x2="90" y2="90" stroke="#96A" />}
{!this.state.path &&   <Line x1="90" y1="50" x2="50" y2="90" stroke="#96A" />}

<Circle cx="10" cy="90" r="5" stroke="blue" strokeWidth={index[6].toString()}  fill="#ED008C"  onPress={()=>{x.push(6); this.setState({path:x}); index[6]++; console.log(x)}}/>
{!this.state.path &&   <Line x1="10" y1="90" x2="50" y2="90" stroke="#060" />}
<Circle cx="50" cy="90" r="5" stroke="blue" strokeWidth={index[7].toString()}  fill="#ED008C"  onPress={()=>{x.push(7); this.setState({path:x}); index[7]++; console.log(x)}} />
{!this.state.path &&   <Line x1="50" y1="90" x2="90" y2="90" stroke="#060" />}
<Circle cx="90" cy="90" r="5" stroke="blue" strokeWidth={index[8].toString()}  fill="#ED008C"  onPress={()=>{x.push(8); this.setState({path:x}); index[8]++; console.log(this.state.path)}} />


</Svg>
</View>}
      
    {this.state.hand &&  
      <Text style={{position:'relative',fontSize:20,margin:'auto', textAlign:'center', color:'#FFF', fontFamily:'FuturaH', marginTop:'85%', backgroundColor:'#ED008C', padding:'5%', width:'70%', borderRadius:10, alignSelf:'center', elevation:1}} onPress={()=>{this.setState({bgHand:'green'}); this.setState({hand:false})}}>SET HAND</Text>}
    {this.state.pattern &&  
      <Text style={{position:'relative',fontSize:20,margin:'auto', textAlign:'center', color:'#FFF', fontFamily:'FuturaH', marginTop:'-55%', backgroundColor:'#ED008C', padding:'5%', width:'70%', borderRadius:10, alignSelf:'center', elevation:1}} onPress={()=>{this.setState({bgPattern:'green'});this.setState({patternstr:x.toString()}); console.log(this.state.patternstr,"Here"); this.setState({pattern:false})}}>SET PATTERN</Text>}
     {this.state.face &&  
      <Text style={{position:'relative',fontSize:20,margin:'auto', textAlign:'center', color:'#FFF', fontFamily:'FuturaH', marginTop:'85%', backgroundColor:'#ED008C', padding:'5%', width:'70%', borderRadius:10, alignSelf:'center', elevation:1}} onPress={()=>{this.setState({bgFace:'green'}); this.setState({hand:false})}}>SET FACE</Text>} 
   
      <Text style={{position:'relative',fontSize:20,margin:'auto', textAlign:'center', color:'#FFF', fontFamily:'FuturaH', marginTop:'55%', backgroundColor:'#ED008C', padding:'5%', width:'70%', borderRadius:10, alignSelf:'center', elevation:1}} onPress={()=>{this.props.navigation.navigate('Spotify')}}>DONE</Text>
    </View>
    );
    }
    else {
    return <AppLoading />;
    }
  }
}

const styles = StyleSheet.create({
  container: {
    height:'100%',
    position:'relative',
    
  },
  header:{
    height:'30%',
    width:'70%',
    marginTop:'20%',
    resizeMode:'contain',
    alignSelf:'center'
  },
  
});